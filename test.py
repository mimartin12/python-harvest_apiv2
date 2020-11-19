# TODO: REMOVE FROM BRANCH BEFORE MERGE TO MASTER

def assemble_query_string(**kwargs):
    query_string = list()
    for k,v in kwargs.items():
        if v is None:
            continue
        elif type(v) is bool:
            v = str(v).lower()
        query_string.append(f'{k}={v}')
    output_query_string = '&'.join(query_string)
    return output_query_string

def tasks(**kwargs):
    baseurl = '/tasks?'
    query_string = assemble_query_string(**kwargs)
    print(baseurl+query_string)

if __name__ == "__main__":
    tasks(page=1, per_page=100, is_active=False, updated_since="2020/11/10", client_id="123456")