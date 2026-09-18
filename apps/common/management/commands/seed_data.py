from django.core.management.base import BaseCommand
from django.db import transaction
from apps.users.models import User, Company, Branch, Employee, Designation
from apps.department.models import Department
from apps.attendance.models import Attendance
from apps.holidays.models import Holiday
from apps.notice.models import Notic, NoticeType
from datetime import date, timedelta, datetime
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed database with sample data for testing"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Starting database seeding..."))

        try:
            with transaction.atomic():
                # 1. Create Company
                company, created = Company.objects.get_or_create(
                    name="Tech Solutions Pvt. Ltd.",
                    defaults={
                        "code": "TECH001",
                        "email": "info@techsolutions.com",
                        "phone": "9876543210",
                        "address": "Thamel, Kathmandu",
                        "city": "Kathmandu",
                        "state": "Bagmati",
                        "country": "Nepal",
                        "registration_number": "REG-001",
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Created company: {company.name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"• Company already exists: {company.name}")
                    )

                # 2. Create Branch
                branch, created = Branch.objects.get_or_create(
                    name="Head Office",
                    company=company,
                    defaults={
                        "code": "HQ01",
                        "address": "Thamel, Kathmandu",
                        "city": "Kathmandu",
                        "phone": "9876543211",
                    },
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Created branch: {branch.name}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"• Branch already exists: {branch.name}")
                    )

                # 3. Create Departments
                departments_data = [
                    {"name": "Engineering", "code": "ENG", "description": "Software Development Team"},
                    {
                        "name": "Human Resources",
                        "code": "HR",
                        "description": "HR and Admin Department",
                    },
                    {"name": "Sales", "code": "SALES", "description": "Sales and Marketing Team"},
                    {"name": "Finance", "code": "FIN", "description": "Finance and Accounting"},
                ]

                departments = {}
                for dept_data in departments_data:
                    dept, created = Department.objects.get_or_create(
                        name=dept_data["name"],
                        company=company,
                        branch=branch,
                        defaults={
                            "code": dept_data["code"],
                            "description": dept_data["description"]
                        },
                    )
                    departments[dept_data["name"]] = dept
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Created department: {dept.name}")
                        )

                # 4. Create Designations
                designations_data = [
                    {
                        "title": "CEO",
                        "code": "CEO",
                        "department": "Engineering",
                        "description": "Chief Executive Officer",
                        "level": 1,
                    },
                    {
                        "title": "Engineering Manager",
                        "code": "ENGMGR",
                        "department": "Engineering",
                        "description": "Engineering Team Lead",
                        "level": 2,
                    },
                    {
                        "title": "Senior Developer",
                        "code": "SRDEV",
                        "department": "Engineering",
                        "description": "Senior Software Developer",
                        "level": 3,
                    },
                    {
                        "title": "Junior Developer",
                        "code": "JRDEV",
                        "department": "Engineering",
                        "description": "Junior Software Developer",
                        "level": 4,
                    },
                    {
                        "title": "HR Manager",
                        "code": "HRMGR",
                        "department": "Human Resources",
                        "description": "Human Resources Manager",
                        "level": 2,
                    },
                    {
                        "title": "HR Executive",
                        "code": "HREXEC",
                        "department": "Human Resources",
                        "description": "HR Executive",
                        "level": 3,
                    },
                ]

                designations = {}
                for desig_data in designations_data:
                    desig, created = Designation.objects.get_or_create(
                        title=desig_data["title"],
                        company=company,
                        department=departments[desig_data["department"]],
                        defaults={
                            "code": desig_data["code"],
                            "description": desig_data["description"],
                            "level": desig_data["level"],
                        },
                    )
                    designations[desig_data["title"]] = desig
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Created designation: {desig.title}")
                        )

                # 5. Create Users and Employees
                users_data = [
                    {
                        "username": "admin",
                        "email": "admin@techsolutions.com",
                        "first_name": "Admin",
                        "last_name": "User",
                        "password": "admin123",
                        "role": "ADMIN",
                        "employee": {
                            "employee_id": "EMP001",
                            "designation": "CEO",
                            "department": "Engineering",
                            "phone_number": "9876543210",
                            "personal_email": "admin@techsolutions.com",
                            "date_of_joining": date(2023, 1, 1),
                            "date_of_birth": date(1985, 5, 15),
                        },
                    },
                    {
                        "username": "manager",
                        "email": "manager@techsolutions.com",
                        "first_name": "Ram",
                        "last_name": "Sharma",
                        "password": "manager123",
                        "role": "MANAGER",
                        "employee": {
                            "employee_id": "EMP002",
                            "designation": "Engineering Manager",
                            "department": "Engineering",
                            "phone_number": "9876543211",
                            "personal_email": "manager@techsolutions.com",
                            "date_of_joining": date(2023, 2, 1),
                            "date_of_birth": date(1988, 8, 20),
                        },
                    },
                    {
                        "username": "employee1",
                        "email": "sita@techsolutions.com",
                        "first_name": "Sita",
                        "last_name": "Rai",
                        "password": "employee123",
                        "role": "EMPLOYEE",
                        "employee": {
                            "employee_id": "EMP003",
                            "designation": "Senior Developer",
                            "department": "Engineering",
                            "phone_number": "9876543212",
                            "personal_email": "sita@techsolutions.com",
                            "date_of_joining": date(2023, 3, 1),
                            "date_of_birth": date(1990, 3, 10),
                        },
                    },
                    {
                        "username": "employee2",
                        "email": "hari@techsolutions.com",
                        "first_name": "Hari",
                        "last_name": "Thapa",
                        "password": "employee123",
                        "role": "EMPLOYEE",
                        "employee": {
                            "employee_id": "EMP004",
                            "designation": "Junior Developer",
                            "department": "Engineering",
                            "phone_number": "9876543213",
                            "personal_email": "hari@techsolutions.com",
                            "date_of_joining": date(2023, 6, 1),
                            "date_of_birth": date(1995, 7, 25),
                        },
                    },
                    {
                        "username": "hr",
                        "email": "hr@techsolutions.com",
                        "first_name": "Maya",
                        "last_name": "Gurung",
                        "password": "hr123",
                        "role": "HR",
                        "employee": {
                            "employee_id": "EMP005",
                            "designation": "HR Manager",
                            "department": "Human Resources",
                            "phone_number": "9876543214",
                            "personal_email": "hr@techsolutions.com",
                            "date_of_joining": date(2023, 1, 15),
                            "date_of_birth": date(1987, 11, 5),
                        },
                    },
                ]

                employees = {}
                manager_employee = None

                for user_data in users_data:
                    user, created = User.objects.get_or_create(
                        username=user_data["username"],
                        defaults={
                            "email": user_data["email"],
                            "first_name": user_data["first_name"],
                            "last_name": user_data["last_name"],
                            "role": user_data["role"],
                            "company": company,
                        },
                    )

                    if created:
                        user.set_password(user_data["password"])
                        user.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Created user: {user.username} (password: {user_data['password']})"
                            )
                        )

                    # Create employee profile
                    emp_data = user_data["employee"]
                    employee, emp_created = Employee.objects.get_or_create(
                        user=user,
                        defaults={
                            "employee_id": emp_data["employee_id"],
                            "company": company,
                            "branch": branch,
                            "department": departments[emp_data["department"]],
                            "designation": designations[emp_data["designation"]],
                            "phone_number": emp_data["phone_number"],
                            "personal_email": emp_data["personal_email"],
                            "date_of_joining": emp_data["date_of_joining"],
                            "date_of_birth": emp_data["date_of_birth"],
                            "gender": "M",
                            "marital_status": "SINGLE",
                            "employment_status": "ACTIVE",
                            "emergency_contact_name": "Emergency Contact",
                            "emergency_contact_phone": "9876543200",
                            "emergency_contact_relation": "Family",
                            "permanent_address": "Kathmandu, Nepal",
                            "current_address": "Kathmandu, Nepal",
                        },
                    )

                    employees[user_data["username"]] = employee

                    if user_data["role"] == "MANAGER":
                        manager_employee = employee

                    if emp_created:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✓ Created employee: {employee.name} ({employee.employee_id})"
                            )
                        )

                # Set manager for employees
                if manager_employee:
                    Employee.objects.filter(
                        employee_id__in=["EMP003", "EMP004"]
                    ).update(manager=manager_employee)
                    self.stdout.write(
                        self.style.SUCCESS(
                            "✓ Assigned manager to employee1 and employee2"
                        )
                    )

                # 6. Create Sample Attendance Records
                today = date.today()
                for i in range(7):  # Last 7 days
                    attendance_date = today - timedelta(days=i)

                    for username, employee in employees.items():
                        # Create attendance for all employees
                        check_in_time = timezone.make_aware(
                            datetime.combine(
                                attendance_date, datetime.strptime("09:00", "%H:%M").time()
                            )
                        )
                        check_out_time = timezone.make_aware(
                            datetime.combine(
                                attendance_date, datetime.strptime("18:00", "%H:%M").time()
                            )
                        )

                        # Skip creating if it's today (let them clock in)
                        if i == 0:
                            continue

                        attendance, created = Attendance.objects.get_or_create(
                            employee=employee,
                            date=attendance_date,
                            defaults={
                                "check_in": check_in_time,
                                "check_out": check_out_time,
                                "status": Attendance.EmployeeStatus.PRESENT,
                                "is_approved": i > 2,  # Approve older records
                                "approved_by": (
                                    User.objects.get(username="manager")
                                    if i > 2
                                    else None
                                ),
                                "approved_at": (
                                    timezone.make_aware(
                                        datetime.combine(
                                            attendance_date + timedelta(days=1),
                                            datetime.strptime("10:00", "%H:%M").time(),
                                        )
                                    )
                                    if i > 2
                                    else None
                                ),
                            },
                        )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS("✓ Created sample attendance records")
                    )

                # 7. Create Holidays
                holidays_data = [
                    {
                        "name": "Dashain Festival",
                        "date": date(2026, 10, 15),
                        "description": "Major Hindu festival",
                    },
                    {
                        "name": "Tihar Festival",
                        "date": date(2026, 11, 3),
                        "description": "Festival of Lights",
                    },
                    {
                        "name": "New Year",
                        "date": date(2027, 1, 1),
                        "description": "New Year Celebration",
                    },
                ]

                for holiday_data in holidays_data:
                    holiday, created = Holiday.objects.get_or_create(
                        name=holiday_data["name"],
                        date=holiday_data["date"],
                        defaults={
                            "description": holiday_data["description"],
                            "branch": branch,
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Created holiday: {holiday.name}")
                        )

                # 8. Create Notice Types and Notices
                notice_type, created = NoticeType.objects.get_or_create(
                    type_name="General",
                    defaults={"description": "General announcements"},
                )

                notices_data = [
                    {
                        "name": "Office Timing Change",
                        "date": today + timedelta(days=7),
                        "description": "Office timing will be changed from next week",
                    },
                    {
                        "name": "Team Meeting",
                        "date": today + timedelta(days=2),
                        "description": "Monthly team meeting scheduled",
                    },
                ]

                for notice_data in notices_data:
                    notice, created = Notic.objects.get_or_create(
                        name=notice_data["name"],
                        date=notice_data["date"],
                        defaults={
                            "description": notice_data["description"],
                            "branch": branch,
                        },
                    )
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"✓ Created notice: {notice.name}")
                        )

                self.stdout.write(
                    self.style.SUCCESS("\n" + "=" * 60)
                )
                self.stdout.write(
                    self.style.SUCCESS("Database seeding completed successfully! 🎉")
                )
                self.stdout.write(
                    self.style.SUCCESS("=" * 60)
                )
                self.stdout.write(self.style.SUCCESS("\nLogin Credentials:"))
                self.stdout.write(
                    self.style.SUCCESS("-" * 60)
                )
                self.stdout.write(
                    self.style.WARNING(
                        "\n1. Admin User:\n   Username: admin\n   Password: admin123"
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        "\n2. Manager User:\n   Username: manager\n   Password: manager123"
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        "\n3. HR User:\n   Username: hr\n   Password: hr123"
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        "\n4. Employee 1:\n   Username: employee1\n   Password: employee123"
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        "\n5. Employee 2:\n   Username: employee2\n   Password: employee123"
                    )
                )
                self.stdout.write(
                    self.style.SUCCESS("\n" + "=" * 60 + "\n")
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error during seeding: {str(e)}")
            )
            raise e
