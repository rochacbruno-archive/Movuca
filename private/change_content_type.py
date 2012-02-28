#coding: utf-8

sqlcommands = []

sqlcommands.append(
 """CREATE TABLE content_type2(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title CHAR(512) NOT NULL,
    description CHAR(512),
    identifier CHAR(512) NOT NULL UNIQUE,
    classname CHAR(512) NOT NULL,
    tablename CHAR(512) NOT NULL,
    viewname CHAR(512),
    childs INTEGER NOT NULL DEFAULT 1,
    is_active CHAR(1),
    created_on TIMESTAMP,
    created_by INTEGER REFERENCES auth_user(id) ON DELETE CASCADE,
    modified_on TIMESTAMP,
    modified_by INTEGER REFERENCES auth_user(id) ON DELETE CASCADE
);""")

sqlcommands.append(
"""INSERT INTO content_type2 (id,  title, description, identifier, classname, tablename, viewname, childs, is_active)
    SELECT id,  title, description, identifier, classname, tablename, viewname, childs, is_active FROM content_type;""")

sqlcommands.append("""ALTER TABLE content_type RENAME TO content_type_old;""")

sqlcommands.append("""ALTER TABLE content_type2 RENAME TO content_type;""")
