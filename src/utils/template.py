receiver_template_0 = """
【Background】
You are an expert in the field of finance and database
Your task is to determine whether answering the user question requires querying databases
【Requirements】
- If you need to get the database schema to make a decision, you don't need to output any text, just make a "function calling"
- If not for the previous case, you can output your answer directly

【Question】
{}
【Answer】
"""

receiver_template_1 = """
【Background】
You are an expert in the field of finance and database
Given the 【Schema】, your task is to determine whether answering the user question requires querying databases
【Requirements】
- If you need to query the database to answer, you don't need to output any text, just make a "function calling"
- If not for the previous case, you can output your answer directly

【Question】
{}
【Schema】
{}
【Answer】
"""

filter_template = """
【Background】
As an experienced and professional database administrator
Your task is to analyze a user question and a database schema to provide relevant information. 
The database schema consists of table descriptions, each containing multiple column descriptions. 
Your goal is to identify the relevant tables and columns based on the user question and evidence provided.

【Requirements】
- If all columns of a table need to be kept, mark it as "keep_all".
- If a table is completely irrelevant to the user question and evidence, mark it as "drop_all".
- If not for the previous two cases, sort the columns in each relevant table in descending order of relevance, determine which columns need to be kept.
- You don't need to give any explanation, just output the answer in JSON format.

==========
Here is a typical example:

【Schema】
=====
Table: basic_info
Column: [
(stk_code, Comment: securities code. Types: text. Primary key.),
(stk_name, Comment: securities name. Types: text.)
]
=====
Table: balance_sheet,
Column: [
(stk_code, Comment: securities code. Types: text.),
(cash_cb, Comment: cash and deposits with central bank. Types: real.),
(ib_deposits, Comment: due from interbank deposits. Types: real.),
(prec_metals, Comment: noble metal. Types: real.),
(lending_funds, Comment: lending funds. Types: real.),
(trad_fas, Comment: trading financial assets. Types: real.),
]
=====
Table: income_statement,
Column: [
(stk_code, Comment: securities code. Types: text.),
(oper_rev, Comment: operating income. Types: real.),
(net_int_inc, Comment: net interest income. Types: real.),
(fee_com_net_inc, Comment: net income from handling fees and commissions. Types: real.),
(fee_com_inc, Comment: fee and commission income. Types: real.),
(fee_com_exp, Comment: handling fees and commission expenses. Types: real.),
]

【Question】
What is the fee and commission income of China Construction Bank in millions of yuan?

【Answer】
```json
{{
  "basic_info": "keep_all",
  "balance_sheet": "drop_all",
  "income_statement": ["stk_code", "fee_com_inc"],
}}
```

==========
Here is a new example, considering 【Requirements】, please start answering:

【Schema】
{}
【Evidence】
{}
【Question】
{}
【Answer】
"""

decompose_template = """
【Background】
Given a 【Schema】 description, a knowledge 【Evidence】 and the 【Question】, you need to use valid SQLite and understand the database and knowledge, and then decompose the question into subquestions for text-to-SQL generation.

【Requirements】
- Keep your answers brief
- When you have generated an SQL statement that already solves the problem, there is no need to generate more text

【Constraints】
When generating SQL, we should always consider constraints:
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

==========
Here is a typical example:

【Schema】
=====
Table: basic_info
Column: [
(stk_code, Comment: securities code. Types: text. Primary key.),
(stk_name, Comment: securities name. Types: text.)
]
=====
Table: balance_sheet,
Column: [
(stk_code, Comment: securities code. Types: text.),
(cash_cb, Comment: cash and deposits with central bank. Types: real.),
]
【Question】
List securities codes and securities names with cash and deposits with central bank over the average.

Decompose the question into sub questions, considering 【Requirements】 and 【Constraints】, and generate the SQL after thinking step by step:
【Answer】
Sub question 1: Get the average value of cash and deposits with central bank.
SQL
```sql
SELECT AVG(cash_cb) FROM balance_sheet
```

Sub question 2: List securities codes and securities names with cash and deposits with central bank over the average.
SQL
```sql
SELECT b2.stk_code,stk_name 
FROM balance_sheet AS b1 INNER JOIN basic_info AS b2 
ON b1.stk_code = b2.stk_code
WHERE cash_cb > (SELECT AVG(cash_cb) FROM balance_sheet)
```
This SQL statement already solves the problem, so there is no need to continue generating text.

==========
Here is a new example, please start answering:

【Schema】
{}
【Evidence】
{}
【Question】
{}

Decompose the question into sub questions, considering 【Requirements】 and 【Constraints】, and generate the SQL after thinking step by step:
【Answer】
"""

reviser_template = """
【Background】
When executing SQL below, some errors occurred, please fix up SQL and generate new SQL based on the information given.
Solve the task step by step if you need to. When you find an answer, verify the answer carefully. 

【Constraints】
When generating SQL, we should always consider constraints:
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

【Schema】
{}

【Evidence】
{}

【Question】
{}

【old SQL】
```sql
{}
```

【SQLite error】 
{}

【Exception class】
{}

Now please fix up old SQL and generate new SQL again.
The format of the new SQL is as follows.
```sql

```
【correct SQL】
"""
