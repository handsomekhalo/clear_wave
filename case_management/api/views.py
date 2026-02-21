


# @api_view(['GET'])
# @permission_classes([CanAccessCase])
# def case_detail(request, pk):
#     case = get_object_or_404(Case, pk=pk)

#     permission = CanAccessCase()
#     if not permission.has_object_permission(request, None, case):
#         return Response(status=403)

#     serializer = CaseSerializer(case)
#     return Response(serializer.data)