from hutch_bunny.core.rquest_dto.query import AvailabilityQuery

class CustomAvailabilityQuery(AvailabilityQuery):
    def __init__(self, *args, **kwargs):
        # Convert collection to list if it's not already
        if 'collection' in kwargs:
            kwargs['collection'] = [kwargs['collection']] if not isinstance(kwargs['collection'], list) else kwargs['collection']
        super().__init__(*args, **kwargs)
    
    def to_dict(self):
        data = super().to_dict()
        # Ensure collection is a list in the output
        if 'collection' in data:
            data['collection'] = [data['collection']] if not isinstance(data['collection'], list) else data['collection']
        return data
