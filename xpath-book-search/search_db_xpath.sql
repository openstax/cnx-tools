create or replace function find_xpath(xpath_str text, file_name text) returns table(uuid uuid, bool boolean) as
$$
begin
        return query
        select m.uuid, xpath_exists(xpath_str, convert_from(file,'utf8')::xml, 
	        	ARRAY [
	                ARRAY ['cnx', 'http://cnx.rice.edu/cnxml'],
	                ARRAY ['md', 'http://cnx.rice.edu/mdml/0.4'],
	                ARRAY ['m','http://www.w3.org/1998/Math/MathML']
	             ]
             )
        from modules m
        natural join module_files
        natural join files
        where filename = file_name;
exception when others then
--ignore the malformed xml doc
end
$$
language plpgsql;

create or replace function get_books_containing_uuid_versionless(input_uuid uuid) RETURNS table(name text, uuid uuid, root_page_uuid uuid, authors text[])
AS
$$
BEGIN
return query
WITH RECURSIVE t(node, title, parent, path, value, root_page_uuid, authors) AS (
        SELECT nodeid, title, parent_id, ARRAY[nodeid], documentid, m.uuid, m.authors
        FROM trees tr, modules m
        WHERE m.uuid = input_uuid
        AND tr.documentid = m.module_ident
        AND tr.parent_id IS NOT NULL
UNION ALL
        SELECT c1.nodeid, c1.title, c1.parent_id, t.path || ARRAY[c1.nodeid], c1.documentid, t.root_page_uuid, t.authors /* Recursion */
        FROM trees c1
        JOIN t ON (c1.nodeid = t.parent)
        WHERE not nodeid = any (t.path)
)
SELECT m.name, m.uuid, t.root_page_uuid, t.authors
FROM t
JOIN modules m on t.value = m.module_ident
WHERE t.parent IS NULL;
END
$$
language plpgsql;

create or replace function get_result(xpath_str text, file_name text) returns table(name text, uuid uuid, root_page_uuid uuid, authors text[], bool boolean)
AS
$$
BEGIN
RETURN QUERY
        select distinct gb.name, gb.uuid, gb.root_page_uuid, gb.authors, fx.bool
        from find_xpath(xpath_str, file_name) AS fx,
        LATERAL get_books_containing_uuid_versionless(fx.uuid) gb;
END
$$
language plpgsql;

create or replace function search_db_xpath(xpath_str text, file_name text) returns table(name text, uuid uuid, root_page_uuid uuid, authors text[])
AS
$$
BEGIN
RETURN QUERY
        select gr.name, gr.uuid, gr.root_page_uuid, gr.authors
        from get_result(xpath_str, file_name) as gr
        where gr.bool = 't';
END
$$
language plpgsql;
