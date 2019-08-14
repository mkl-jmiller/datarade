select
    s.name as schema_name,
    t.name as table_name
from SANDBOX.sys.tables t
join SANDBOX.sys.schemas s
    on s.schema_id = t.schema_id
