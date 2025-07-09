# Resources management

Each routes does not represents its resource. For example, we implement a statistics folder or a learning folder that represents other resources.

## Country

We decided to import the country data at startup of the db. 

For this route we just implement the Read.

## Dictionary

For this route we implement a CRUD. 

- User can add / read / delete /update his dictionaries.
- Admin user can Update and Delete others dictionaries.

## Entry

For this route, we implement a CRUD. 

- User can Create / Read / Update / Delete his entries
- Admin can Delete entries.

## Language

For this route we implement a CRD. 

- User can Create / Read languages
- Admin can Delete a Language.

## User

For this route we implement a CRUD for the user resource. 

We also implement the get_dictionary logic in order to keep a logic in the url.

The read_me function allows the frontend to get user informations. 

We also implement signin / signup functions here. 

