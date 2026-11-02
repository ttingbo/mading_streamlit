import streamlit as st
import pandas as pd
import psycopg2

st.title("마당서점 주문 조회")

name = st.text_input("고객 이름")

if st.button("검색"):
    name = name.strip()

    if not name:
        st.warning("고객 이름을 입력해주세요.")
        st.stop()

    try:
        db_url = st.secrets["DATABASE_URL"]
    except (FileNotFoundError, KeyError):
        st.info("DB 연결 설정 전입니다. Neon 설정 후 검색할 수 있습니다.")
        st.stop()

    dbConn = None

    try:
        dbConn = psycopg2.connect(db_url, connect_timeout=10)
        cursor = dbConn.cursor()

        sql = """
            SELECT o.orderid, c.name, b.bookname,
                   o.saleprice, o.orderdate
            FROM Customer c, Orders o, Book b
            WHERE c.name = %s
              AND c.custid = o.custid
              AND b.bookid = o.bookid
            ORDER BY o.orderid;
        """

        cursor.execute(sql, (name,))
        result = cursor.fetchall()

        result = pd.DataFrame(
            result,
            columns=["orderid", "name", "bookname",
                     "saleprice", "orderdate"]
        )

        if result.empty:
            st.info("조회된 주문 내역이 없습니다.")
        else:
            st.dataframe(result, hide_index=True)

        cursor.close()

    except psycopg2.Error as e:
        print(e)
        st.error("DB 조회에 실패했습니다. 터미널의 오류 내용을 확인해주세요.")

    finally:
        if dbConn is not None:
            dbConn.close()