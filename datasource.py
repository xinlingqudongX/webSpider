from peewee import DateTimeField, CharField, BooleanField, TextField, Model


class MiniTask(Model):
    '''微型任务'''

    created_at = DateTimeField() 
    updated_at = DateTimeField() 
    link = CharField() 
    domain = CharField() 
    is_completed = BooleanField() 
    page_data = TextField()
    origin_link = CharField()
    '''来源链接'''

class SpiderTask(Model):
    '''爬虫任务'''
    created_at = DateTimeField() 
    updated_at = DateTimeField() 
    link = CharField() 
    domain = CharField() 
    is_completed = BooleanField() 
    page_data = TextField()

class PersonnelInfo(Model):
    
    user_name = CharField()
    user_gender = CharField()
    user_phone = CharField()
    user_nition = CharField()
    user_desc = CharField()
    user_birth_date = CharField()
    user_location = CharField()
    user_address = CharField()
    
    created_at = DateTimeField() 
    updated_at = DateTimeField() 