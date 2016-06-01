from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError


api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key, value in json_data.items():
            setattr(self, key, value)
        

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        json_data = api_client.get_people(resource_id)
        return cls(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        if cls == People:
            return PeopleQuerySet()
        else:
            return FilmQuerySet()
        

class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return u'Person: {0}'.format(decode(self.name))
        #return u'Person: {0}'.format(self.name.decode('utf-8'))


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return u'Film: {0}'.format(self.title)


class BaseQuerySet(object):
    
    set_to_method = {'people': api_client.get_people, 'films': api_client.get_films}
    set_to_class = {'people': People, 'films': Films}
    
    def __init__(self):
        self.classname = self.set_to_class[self.RESOURCE_NAME]
        self.get_item = self.set_to_method[self.RESOURCE_NAME]
        self.item_count = 1
        self.page_count = 1
        self.list_index = 0
        self.max_items = self.get_item(page=self.page_count)['count']


    def __iter__(self):
        self.item_count = 1
        self.page_count = 1
        self.list_index = 0
        self.max_items = self.get_item(page=self.page_count)['count']
        return self
        

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        if self.item_count > self.max_items:
            raise StopIteration
        
        items = self.get_item(page=self.page_count)['results']
        if self.list_index >= len(items):
            self.list_index = 0
            self.page_count += 1
            items = self.get_item(page=self.page_count)['results']
            
        self.item_count += 1
        
        return self.classname(items[self.list_index])
        
        
        
        

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return sum((1 for item in self))
        



class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return u'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return u'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))

