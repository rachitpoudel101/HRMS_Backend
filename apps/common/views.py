# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from django.apps import apps
# from rest_framework import status


# @api_view(['GET'])
# def get_model_schema(request, app_label, model_name):
#     """
#     Returns metadata about a model including fields, types, and choices.
#     This enables dynamic form generation on the frontend.
#     """
#     try:
#         model = apps.get_model(app_label, model_name)
#     except LookupError:
#         return Response(
#             {'error': f'Model {app_label}.{model_name} not found'},
#             status=status.HTTP_404_NOT_FOUND
#         )
    
#     fields_metadata = []
    
#     for field in model._meta.get_fields():
#         # Skip reverse relations and many-to-many
#         if field.many_to_one or field.one_to_one:
#             if field.name in ['user', 'company', 'branch', 'department', 'designation', 'manager']:
#                 fields_metadata.append({
#                     'name': field.name,
#                     'type': 'foreign_key',
#                     'label': field.verbose_name.title(),
#                     'required': not field.null,
#                     'related_model': f"{field.related_model._meta.app_label}.{field.related_model._meta.model_name}",
#                 })
#         elif field.name in ['id', 'created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by']:
#             continue
#         elif hasattr(field, 'choices') and field.choices:
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'choice',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#                 'choices': [{'value': choice[0], 'label': choice[1]} for choice in field.choices],
#             })
#         elif field.get_internal_type() == 'CharField':
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'text',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#                 'max_length': field.max_length,
#             })
#         elif field.get_internal_type() == 'EmailField':
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'email',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#             })
#         elif field.get_internal_type() == 'DateField':
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'date',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#             })
#         elif field.get_internal_type() == 'DateTimeField':
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'datetime',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#             })
#         elif field.get_internal_type() == 'BooleanField':
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'boolean',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#             })
#         elif field.get_internal_type() == 'TextField':
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'textarea',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#             })
#         elif field.get_internal_type() == 'URLField':
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'url',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#             })
#         elif field.get_internal_type() == 'ImageField':
#             fields_metadata.append({
#                 'name': field.name,
#                 'type': 'image',
#                 'label': field.verbose_name.title(),
#                 'required': not field.null,
#             })
    
#     return Response({
#         'model': f"{app_label}.{model_name}",
#         'fields': fields_metadata,
#     })


# @api_view(['GET'])
# def get_related_options(request, app_label, model_name):
#     """
#     Returns available options for a related field (foreign key).
#     """
#     try:
#         model = apps.get_model(app_label, model_name)
#     except LookupError:
#         return Response(
#             {'error': f'Model {app_label}.{model_name} not found'},
#             status=status.HTTP_404_NOT_FOUND
#         )
    
#     # Get all objects from the model
#     queryset = model.objects.all()
    
#     # Filter by company if the model has a company field
#     if hasattr(model, 'company') and 'company_id' in request.query_params:
#         queryset = queryset.filter(company_id=request.query_params['company_id'])
    
#     options = []
#     for obj in queryset:
#         options.append({
#             'id': obj.pk,
#             'label': str(obj),
#         })
    
#     return Response({'options': options})
