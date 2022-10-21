import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple, Union


# name, id, created, modified
Session = Tuple[str, str, str, str]
# name, start, end, text, session_name, session_id, created, modified
Range = Tuple[str, int, int, str, str, str, str, str]
# name, start, length, text, session_name, session_id, created, modified
Region = Tuple[str, int, int, str, str, str, str, str]
# tag_name, range_name, range_start, range_end
RangeTag = Tuple[str,str, int, int, str, str]
# tag_name, range_name, range_start, range_end
RegionTag = Tuple[str,str, int, int, str, str]
# Tag = Tuple[str, str]


def connect(database: str) -> sqlite3.Connection:
    conn = sqlite3.connect(database=database)
    create_schema(conn)
    # conn.row_factory = sqlite3.Row

    return conn


def create_schema(conn: sqlite3.Connection):
    conn.execute("""
    create table if not exists session (
        name, id, created, modified,
        primary key (name, id)
    )
    """)
    conn.execute("""
    create table if not exists tag (
        name primary key, created
    )
    """)
    conn.execute("""
    create table if not exists range (
        name,
        start,
        end,
        text,
        session_name,
        session_id,
        created,
        modified,
        primary key (
            name,
            start,
            end,
            session_name,
            session_id
        )
    )
    """)
    conn.execute("""
    create table if not exists range_tag (
        tag_name,
        range_name,
        range_start,
        range_end,
        range_session_name,
        range_session_id,
        created,
        primary key (
            tag_name,
            range_name,
            range_start,
            range_end,
            range_session_name,
            range_session_id
        )
    )
    """)
    conn.execute("""
    create table if not exists region (
        name,
        start,
        length,
        text,
        session_name,
        session_id,
        created,
        modified,
        primary key (
            name,
            start,
            length,
            session_name,
            session_id
        )
    )
    """)
    conn.execute("""
    create table if not exists region_tag (
        tag_name,
        region_name,
        region_start,
        region_length,
        region_session_name,
        region_session_id,
        created,
        primary key (
            tag_name,
            region_name,
            region_start,
            region_length,
            region_session_name,
            region_session_id
        )
    )
    """)


def fetch_range(
    conn: sqlite3.Connection,
    session: Session,
    name: str,
    start: int,
    end: int,
) -> Optional[Range]:
    session_name, session_id, *_ = session

    return conn.execute(
        """
        select
            name,
            start,
            end,
            text,
            session_name,
            session_id,
            created,
            modified
        from range
        where
            name = ?
            and start = ?
            and end = ?
            and session_name = ?
            and session_id = ?
        """,
        (name, start, end, session_name, session_id),
    ).fetchone()


def fetch_or_create_range(
    conn: sqlite3.Connection,
    session: Session,
    name: str,
    start: int,
    end: int,
) -> Range:
    existing_range = fetch_range(conn, session, name, start, end)

    if existing_range:
        return existing_range

    session_name, session_id, *_ = session
    created = datetime.utcnow().isoformat()
    range: Range = (
        name,
        start,
        end,
        "",
        session_name,
        session_id,
        created,
        created,
    )
    insert_range(conn, range)

    return range

def fetch_region(
    conn: sqlite3.Connection,
    session: Session,
    name: str,
    start: int,
    length: int,
) -> Optional[Region]:
    session_name, session_id, *_ = session

    return conn.execute(
        """
        select
            name,
            start,
            length,
            text,
            session_name,
            session_id,
            created,
            modified
        from region
        where
            name = ?
            and start = ?
            and length = ?
            and session_name = ?
            and session_id = ?
        """,
        (name, start, length, session_name, session_id),
    ).fetchone()


def fetch_or_create_region(
    conn: sqlite3.Connection,
    session: Session,
    name: str,
    start: int,
    length: int,
) -> Region:
    existing_region = fetch_region(conn, session, name, start, length)

    if existing_region:
        return existing_region

    session_name, session_id, *_ = session
    created = datetime.utcnow().isoformat()
    region: Region = (
        name,
        start,
        length,
        "",
        session_name,
        session_id,
        created,
        created,
    )
    insert_region(conn, region)

    return region


def fetch_region_tags(
    conn: sqlite3.Connection,
    region: Region,
) -> List[RegionTag]:
    name, start, length, _, session_name, session_id, *_ = region

    return conn.execute(
        """
        select
            tag_name,
            region_name,
            region_start,
            region_length,
            region_session_name,
            region_session_id
        from region_tag
        where
            region_name = ?
            and region_start = ?
            and region_length = ?
            and region_session_name = ?
            and region_session_id = ?
        """,
        (name, start, length, session_name, session_id),
    ).fetchall()


def fetch_range_tags(
    conn: sqlite3.Connection,
    range: Range,
) -> List[RangeTag]:
    name, start, end, _, session_name, session_id, *_ = range

    return conn.execute(
        """
        select
            tag_name,
            range_name,
            range_start,
            range_end,
            range_session_name,
            range_session_id
        from range_tag
        where
            range_name = ?
            and range_start = ?
            and range_end = ?
            and range_session_name = ?
            and range_session_id = ?
        """,
        (name, start, end, session_name, session_id),
    ).fetchall()


def update_range(
    conn: sqlite3.Connection,
    range: Range,
):
    name, start, end, text, session_name, session_id, _, modified = range
    conn.execute(
        """
        update range
        set
            text = ?,
            modified = ?
        where
            name = ?
            and start = ?
            and end = ?
            and session_name = ?
            and session_id = ?
        """,
        (text, modified, name, start, end, session_name, session_id),
    )


def insert_range(
    conn: sqlite3.Connection,
    range: Range,
):
    conn.execute(
        """
        insert into range (
            name,
            start,
            end,
            text,
            session_name,
            session_id,
            created,
            modified
        ) values (?,?,?,?,?,?,?,?)
        """,
        range,
    )
    # include range name as first tag on creation of new range
    update_range_tags(conn, range, (range[0],))


def update_region(
    conn: sqlite3.Connection,
    region: Region,
):
    name, start, length, text, session_name, session_id, _, modified = region
    conn.execute(
        """
        update region
        set
            text = ?,
            modified = ?
        where
            name = ?
            and start = ?
            and length = ?
            and session_name = ?
            and session_id = ?
        """,
        (text, modified, name, start, length, session_name, session_id),
    )


def insert_region(
    conn: sqlite3.Connection,
    region: Region,
):
    conn.execute(
        """
        insert into region (
            name,
            start,
            length,
            text,
            session_name,
            session_id,
            created,
            modified
        ) values (?,?,?,?,?,?,?,?)
        """,
        region,
    )
    # include region name as first tag on creation of new region
    update_region_tags(conn, region, (region[0],))


def fetch_session(
    conn: sqlite3.Connection,
    name: str, 
    id: str,
) -> Optional[Session]:
    return conn.execute("""
        select name, id, created, modified
        from session
        where
            name = ?
            and id = ?
        """, (name, id)
    ).fetchone()


def insert_session(conn: sqlite3.Connection, session: Session):
    return conn.execute("""
        insert into session (name, id, created, modified)
        values (?,?,?,?)
        """,
        session
    )


def fetch_or_create_session(
    conn: sqlite3.Connection,
    name: str,
    id: str,
) -> Session:
    existing_session = fetch_session(conn, name, id)

    if existing_session:
        return existing_session

    created = datetime.utcnow().isoformat()
    session: Session = (name, id, created, created)
    insert_session(conn, session)

    return session


def update_range_tags(
    conn: sqlite3.Connection,
    range: Range,
    tag_names: List[str],
):
    name, start, end, _, session_name, session_id, _, modified = range

    # delete the range_tags not currently in `tags`
    conn.execute(
        f"""
        delete from range_tag
        where
            range_name = ?
            and range_start = ?
            and range_end = ?
            and range_session_name = ?
            and range_session_id = ?
            and tag_name not in (
                {",".join("?" for _ in tag_names)}
            )
        """,
        (name, start, end, session_name, session_id, *tag_names),
    )

    conn.executemany(
        """
        insert into tag (name, created)
        select ?,?
        where not exists (select 1 from tag where name = ?)
        """,
        ((tag, modified, tag) for tag in tag_names)
    )

    conn.executemany(
        """
        insert into range_tag (
            tag_name,
            range_name,
            range_start,
            range_end,
            range_session_name,
            range_session_id
        )
        select ?,?,?,?,?,?
        where not exists (
            select 1 from range_tag
            where
                tag_name = ?
                and range_name = ?
                and range_start = ?
                and range_end = ?
                and range_session_name = ?
                and range_session_id = ?
        )
        """,
        (
            [
                param for param in (
                    tag, name, start, end, session_name, session_id
                ) * 2
            ]
            for tag in tag_names
        ),
    )


def clean_tags(conn: sqlite3.Connection):
    conn.execute("""
    delete from tag
    where name not in (
        select tag_name from range_tag
    
        union
    
        select tag_name from region_tag
    )
    """)


def update_region_tags(
    conn: sqlite3.Connection,
    region: Region,
    tag_names: List[str],
):
    name, start, length, _, session_name, session_id, _, modified = region

    # delete the range_tags not currently in `tags`
    conn.execute(
        f"""
        delete from region_tag
        where
            region_name = ?
            and region_start = ?
            and region_length = ?
            and region_session_name = ?
            and region_session_id = ?
            and tag_name not in (
                {",".join("?" for _ in tag_names)}
            )
        """,
        (name, start, length, session_name, session_id, *tag_names),
    )

    conn.executemany(
        """
        insert into tag (name, created)
        select ?,?
        where not exists (select 1 from tag where name = ?)
        """,
        ((tag, modified, tag) for tag in tag_names)
    )

    conn.executemany(
        """
        insert into region_tag (
            tag_name,
            region_name,
            region_start,
            region_length,
            region_session_name,
            region_session_id
        )
        select ?,?,?,?,?,?
        where not exists (
            select 1 from region_tag
            where
                tag_name = ?
                and region_name = ?
                and region_start = ?
                and region_length = ?
                and region_session_name = ?
                and region_session_id = ?
        )
        """,
        (
            [
                param for param in (
                    tag, name, start, length, session_name, session_id
                ) * 2
            ]
            for tag in tag_names
        ),
    )
