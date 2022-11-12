from django.shortcuts import render


class VerificationViewSet(viewsets.ModelViewSet):
    queryset = Verification.objects.all()
    filter_class = VerificationFilter
    permission_classes = [
        rest_framework_permissions.IsAuthenticatedOrReadOnly
    ]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateVerificationSerializer
        else:
        	return GetVerificationSerializer

    def create(self, request, *args, **kwargs):
    	#Validate input
    	serializer = CreateVerificationSerializer(data=request.data)
    	serializer.is_valid(raise_exception=True)

    	#Send API call to SOCAN
    	number = request.data.get('number')
    	legal_name = request.data.get('legal_name')

    	#More to come when this is actually finished

    	#Validate repsponse
    	#Update Verification row
    	return super().create(request, *args, **kwargs)