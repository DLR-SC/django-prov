order_create_pattern = (
    r'document\n'
    r'  default <example\.org/>\n'
    r'  prefix auth <example\.org/auth/>\n'
    r'  prefix django <example\.org/django/>\n'
    r'  prefix sys <example\.org/sys/>\n'
    r'  prefix example <example\.org/example/>\n'
    r'  prefix django_prov <example\.org/django\_prov/>\n  \n'

    r'  entity\(example:Borrowing-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Borrowing\'>", '
    r'example:id="2", example:student_id="1", example:responsible_librarian_id="None", '
    r'example:date_of_order="\d{4}-\d{2}-\d{2}", example:bor_start_date="None", '
    r'example:bor_auto_end_date="None", example:bor_returned_date="None", example:status="O", '
    r'example:note=""\]\)\n'

    r'  entity\(example:Student-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Student\'>", '
    r'example:id="1", example:matrikelnr="1234567", example:person_id="1"\]\)\n'

    r'  agent\(auth:User-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="auth:<class \'django\.contrib\.auth\.models\.User\'>", '
    r'auth:id="1", auth:password="[^"]+", auth:last_login="\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}", '
    r'auth:is_superuser="False", auth:username="Student", auth:first_name="", auth:last_name="", '
    r'auth:email="", auth:is_staff="False", auth:is_active="True", '
    r'auth:date_joined="\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}"\]\)\n'

    r'  wasAttributedTo\(example:Student-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'auth:User-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  hadMember\(example:Borrowing-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Student-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Borrowing_ordered_books-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:example\.Borrowing\.ordered_books", '
    r'example:model="<class \'example\.models\.Borrowing\'>", example:model_id="2", '
    r'example:related_model="<class \'example\.models\.Book\'>"\]\)\n'

    r'  hadMember\(example:Borrowing-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Borrowing_ordered_books-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Borrowing_borrowed_books-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:example\.Borrowing\.borrowed_books", '
    r'example:model="<class \'example\.models\.Borrowing\'>", example:model_id="2", '
    r'example:related_model="<class \'example\.models\.Book\'>"\]\)\n'

    r'  hadMember\(example:Borrowing-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Borrowing_borrowed_books-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  wasGeneratedBy\(example:Borrowing-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'django:foo22-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -\)\n'

    r'  entity\(example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Book\'>", example:id="1", example:isbn="9781627052214", '
    r'example:title="Provenance: An Introduction to PROV", example:author="Luc Moreau", '
    r'example:pub_year="2013", example:is_borrowed="False"\]\)\n'

    r'  hadMember\(example:Borrowing_ordered_books-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Book\'>", example:id="2", '
    r'example:isbn="978140885589", example:title="Harry Potter and the Philosopher\'s Stone", '
    r'example:author="J\.K\. Rowling", example:pub_year="1997", example:is_borrowed="False"\]\)\n'

    r'  hadMember\(example:Borrowing_ordered_books-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  activity\(django:foo22-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}, \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}, '
    r'\[prov:type="django:func functools\.partial\(<bound method View\.dispatch of '  
    r'<example\.views\.OrderCreateView object at 0x[0-9A-Fa-f]+>>\)", '
    r'sys:python_version=".*", '
    r'sys:os=".*", '
    r'sys:os_username=".*", '
    r'django:args-0="<WSGIRequest: POST \'/order/create/\'>", '
    r'django:result="<HttpResponseRedirect status_code=302, \\"text/html; charset=utf-8\\", '
    r'url=\\"/orders/\\">"\]\)\n'

    r'  wasAssociatedWith\(django:foo22-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'auth:User-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -\)\n'

    r'endDocument\n'
)

borrowing_start_pattern = (
r'document\n'
    r'  default <example\.org/>\n'
    r'  prefix auth <example\.org/auth/>\n'
    r'  prefix django <example\.org/django/>\n'
    r'  prefix sys <example\.org/sys/>\n'
    r'  prefix example <example\.org/example/>\n'
    r'  prefix django_prov <example\.org/django_prov/>\n  \n'

    r'  entity\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Borrowing\'>", '
    r'example:id="1", example:student_id="1", example:responsible_librarian_id="None", '
    r'example:date_of_order="\d{4}-\d{2}-\d{2}", example:bor_start_date="None", '
    r'example:bor_auto_end_date="None", example:bor_returned_date="None", example:status="O", '
    r'example:note=""\]\)\n'

    r'  entity\(example:Student-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Student\'>", '
    r'example:id="1", example:matrikelnr="1234567", example:person_id="1"\]\)\n'

    r'  agent\(auth:User-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="auth:<class \'django\.contrib\.auth\.models\.User\'>", '
    r'auth:id="1", auth:password="[^"]+", auth:last_login="\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}", '
    r'auth:is_superuser="False", auth:username="Student", auth:first_name="", auth:last_name="", '
    r'auth:email="", auth:is_staff="False", auth:is_active="True", '
    r'auth:date_joined="\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}"\]\)\n'

    r'  wasAttributedTo\(example:Student-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'auth:User-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  hadMember\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Student-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Borrowing_ordered_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:example\.Borrowing\.ordered_books", '
    r'example:model="<class \'example\.models\.Borrowing\'>", example:model_id="1", '
    r'example:related_model="<class \'example\.models\.Book\'>"\]\)\n'

    r'  hadMember\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Borrowing_ordered_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Book\'>", example:id="1", example:isbn="9781627052214", '
    r'example:title="Provenance: An Introduction to PROV", example:author="Luc Moreau", '
    r'example:pub_year="2013", example:is_borrowed="False"\]\)\n'

    r'  hadMember\(example:Borrowing_ordered_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Book\'>", example:id="2", '
    r'example:isbn="978140885589", example:title="Harry Potter and the Philosopher\'s Stone", '
    r'example:author="J\.K\. Rowling", example:pub_year="1997", example:is_borrowed="False"\]\)\n'

    r'  hadMember\(example:Borrowing_ordered_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Borrowing_borrowed_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:example\.Borrowing\.borrowed_books", '
    r'example:model="<class \'example\.models\.Borrowing\'>", example:model_id="1", '
    r'example:related_model="<class \'example\.models\.Book\'>"\]\)\n'

    r'  hadMember\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Borrowing_borrowed_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  wasDerivedFrom\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -, -, -\)\n'

    r'  hadMember\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Student-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Librarian-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Librarian\'>", example:id="1", example:person_id="2"\]\)\n'

    r'  agent\(auth:User-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="auth:<class \'django\.contrib\.auth\.models\.User\'>", '
    r'auth:id="2", auth:password="[^"]+", auth:last_login="\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}", '
    r'auth:is_superuser="False", auth:username="Librarian", auth:first_name="", auth:last_name="", '
    r'auth:email="", auth:is_staff="False", auth:is_active="True", '
    r'auth:date_joined="\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}"\]\)\n'

    r'  wasAttributedTo\(example:Librarian-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'auth:User-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  hadMember\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Librarian-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Borrowing_ordered_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:example\.Borrowing\.ordered_books", '
    r'example:model="<class \'example\.models\.Borrowing\'>", example:model_id="1", '
    r'example:related_model="<class \'example\.models\.Book\'>"\]\)\n'

    r'  hadMember\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Borrowing_ordered_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  hadMember\(example:Borrowing_ordered_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  hadMember\(example:Borrowing_ordered_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  entity\(example:Borrowing_borrowed_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:example\.Borrowing\.borrowed_books", '
    r'example:model="<class \'example\.models\.Borrowing\'>", example:model_id="1", '
    r'example:related_model="<class \'example\.models\.Book\'>"\]\)\n'

    r'  hadMember\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Borrowing_borrowed_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  wasGeneratedBy\(example:Borrowing-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'django:foo23-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -\)\n'

    r'  entity\(example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Book\'>", example:id="1", '
    r'example:isbn="9781627052214", example:title="Provenance: An Introduction to PROV", '
    r'example:author="Luc Moreau", example:pub_year="2013", example:is_borrowed="True"\]\)\n'

    r'  wasDerivedFrom\(example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -, -, -\)\n'

    r'  wasGeneratedBy\(example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'django:foo23-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -\)\n'

    r'  entity\(example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\[prov:type="example:<class \'example\.models\.Book\'>", example:id="2", '
    r'example:isbn="978140885589", example:title="Harry Potter and the Philosopher\'s Stone", '
    r'example:author="J\.K\. Rowling", example:pub_year="1997", example:is_borrowed="True"\]\)\n'

    r'  wasDerivedFrom\(example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -, -, -\)\n'

    r'  wasGeneratedBy\(example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'django:foo23-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -\)\n'

    r'  hadMember\(example:Borrowing_borrowed_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  hadMember\(example:Borrowing_borrowed_books-1-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'example:Book-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}\)\n'

    r'  activity\(django:foo23-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}, \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}, '
    r'\[prov:type="django:func functools\.partial\(<bound method View\.dispatch of <example\.views\.BorrowStartView object at 0x[0-9A-Fa-f]+>>\)", '
    r'sys:python_version="3\.9\.1 \(tags/v3\.9\.1:1e5d33e, Dec  7 2020, 17:08:21\) \[MSC v\.1927 64 bit \(AMD64\)\]", '
    r'sys:os="Windows-10-10\.0\.19041-SP0", sys:os_username="baue_bn", '
    r'django:args-0="<WSGIRequest: POST \'/borrowing/start/1\'>", django:kwargs-0-pk="1", '
    r'django:result="<HttpResponseRedirect status_code=302, \\"text/html; charset=utf-8\\", url=\\"/borrowings/\\">"\]\)\n'

    r'  wasAssociatedWith\(django:foo23-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, '
    r'auth:User-2-\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}-\d{6}, -\)\n'
    r'endDocument'
)

test_handle_m2m_changed_pattern = (
    r'document\n'
    r'  default <example\.org/>\n'
    r'  prefix auth <example\.org/auth/>\n'
    r'  prefix django <example\.org/django/>\n'
    r'  prefix sys <example\.org/sys/>\n'
    r'  prefix example <example\.org/example/>\n'
    r'  prefix django_prov <example\.org/django_prov/>\n  \n'

    r'  entity\(example:Borrowing-1-.*\)\n'
    r'  entity\(example:Student-1-.*\)\n'
    r'  agent\(auth:User-1-.*\)\n'
    r'  wasAttributedTo\(example:Student-1-.*, auth:User-1-.*\)\n'
    r'  hadMember\(example:Borrowing-1-.*, example:Student-1-.*\)\n'
    r'  entity\(example:Borrowing_ordered_books-1-.*\)\n'
    r'  hadMember\(example:Borrowing-1-.*, example:Borrowing_ordered_books-1-.*\)\n'
    r'  entity\(example:Book-1-.*\)\n'
    r'  hadMember\(example:Borrowing_ordered_books-1-.*, example:Book-1-.*\)\n'
    r'  entity\(example:Borrowing_borrowed_books-1-.*\)\n'
    r'  hadMember\(example:Borrowing-1-.*, example:Borrowing_borrowed_books-1-.*\)\n'
    r'endDocument'
)


test_create_prov_record_student_pattern = (
    r'entity\(example:Student-1-.*, \[prov:type="example:\<class \'example\.models\.Student\'>", example:id="1", example:matrikelnr="1234567", example:person\_id="1"\]\)',
    r'agent\(auth:User-1-.*, \[prov:type="auth:<class \'django.contrib.auth.models.User\'>", auth:id="1", auth:password=".*", auth:last_login="None", auth:is_superuser="False", auth:username="Student", auth:first_name="", auth:last_name="", auth:email="", auth:is_staff="False", auth:is_active="True", auth:date_joined=".*"\]\)',
    r'wasAttributedTo\(example:Student-1-.*, auth:User-1-.*\)'
)
