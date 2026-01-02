class CompanyFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        request = getattr(self, 'request', None)
        if request and hasattr(request, 'query_params'):
            company_id = request.query_params.get('company_id')
            company_name = request.query_params.get('company_name')
            if company_id:
                queryset = queryset.filter(company__id=company_id)
            if company_name:
                queryset = queryset.filter(company__name__iexact=company_name)
        return queryset
