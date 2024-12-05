filter_template = """
As an experienced and professional database administrator, your task is to analyze a user question and a database schema to provide relevant information. 
The database schema consists of table descriptions, each containing multiple column descriptions. 
Your goal is to identify the relevant tables and columns based on the user question and evidence provided.

【Requirements】
1. If all columns of a table need to be kept, mark it as "keep_all".
2. If a table is completely irrelevant to the user question and evidence, mark it as "drop_all".
3. If not for the previous two cases, sort the columns in each relevant table in descending order of relevance, determine which columns need to be kept.
4. The output should be in JSON format.

Here is a typical example:

==========
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
Question Solved.

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
Given a 【Database schema】 description, a knowledge 【Evidence】 and the 【Question】, you need to use valid SQLite and understand the database and knowledge, and then decompose the question into subquestions for text-to-SQL generation.
When generating SQL, we should always consider constraints:

【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

Here is a typical example:

==========
【Database schema】
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

Decompose the question into sub questions, considering 【Constraints】, and generate the SQL after thinking step by step:
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

Question Solved.

==========

【Database schema】
{}
【Evidence】
{}
【Question】
{}

Decompose the question into sub questions, considering 【Requirements】, and generate the SQL after thinking step by step:
"""

reviser_template = """
【Instruction】
When executing SQL below, some errors occurred, please fix up SQL based on query and database info.
Solve the task step by step if you need to. Using SQL format in the code block, and indicate script type in the code block.
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.

【Constraints】
- In `SELECT <column>`, just select needed columns in the 【Question】 without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If [Value examples] of <column> has 'None' or None, use `JOIN <table>` or `WHERE <column> is NOT NULL` is better
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

【Query】
{}

【Database info】
{}

【old SQL】
```sql
{}
```

【SQLite error】 
{}

【Exception class】
{}

Now please fixup old SQL and generate new SQL again.
The format of the new SQL is as follows.
```sql

```
【correct SQL】
"""
