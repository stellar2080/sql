extractor_template = """
You are an expert in the field of finance and database.
You need to follow the instructions below to solve the problem step by step:
1. Identify and extract any key entities from the text that can help with financial database queries
2. Format the answer in the same Python list format as the [Answer] part of the example

Example:
[Text]
I want to know the working capital and current ratio of Huaxia Bank.
[Hint]
Here are some entity names for reference:
{{'Total Assets', 'Working capital', 'Current ratio', 'current assets', 'return on assets'}}
[Answer]
['working capital','current ratio','Huaxia Bank']

Please start solving the problem:
[Text]
{}
[Hint]
Here are some entity names for reference:
{}
"""

filter_template = """
[Task]
You are an expert in the field of finance and database. 
Given a user question and a database schema consisting of table descriptions, each table contains multiple column descriptions.
Your task is to select relevant tables and columns based on user question and hint provided.

[Requirements]
- Your final answer should be in the same JSON format as the example given
- Solve the task step by step
- Don't use code

Here is a typical example:
[Schema]
=====
Table: basic_info
Column:
(Stk_code, Comment: Securities code, Type: TEXT, Primary key)
(Stk_name, Comment: Securities name, Type: TEXT, Sample: Huaxia Bank)
=====
Table: balance_sheet
Column:
(Stk_code, Comment: Securities code, Type: TEXT, Foreign key: references Basic_Info(Stk_Code))
=====
Table: income_statement
Column:
(Stk_code, Comment: Securities code, Type: TEXT, Foreign key: references Basic_Info(Stk_Code))
(Fee_com_inc, Comment: Fee and commission income, Type: REAL)
(Fee_com_exp, Comment: Handling fees and commission expenses, Type: REAL)
[Question]
What is the fee and commission income of Huaxia Bank?
[Answer]
{{
  "basic_info": ["Stk_code","Stk_name"],
  "balance_sheet": [],
  "income_statement": ["Stk_code","Fee_com_inc"],
}}

Here is a new example, please start answering:
[Schema]
{}
[Question]
{}
"""

filter_hint_template = """[Hint]
You can refer to following information to solve the task:
{}
"""


decomposer_template = """
[Task]
You are an experienced financial database administrator.
Given a database schema, a hint and a question.
Your task is to decompose the question into subquestions and use the SQLite dialect for text-to-SQL generation.

[Requirements]
- When you have generated an SQL statement that already solves the problem, there is no need to generate more text

[SQL Constraints]
When generating SQL, we should always consider constraints:
- In `SELECT <column>`, just select needed columns in the [Question] without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

==========
Here is a typical example:

[Schema]
=====
Table: basic_info
Column:
(Stk_code, Comment: Securities code, Type: TEXT, Primary key)
(Stk_name, Comment: Securities name, Type: TEXT)
=====
Table: balance_sheet
Column:
(Stk_code, Comment: Securities code, Type: TEXT, Foreign key: references Basic_Info(Stk_Code))
(Cash_cb, Comment: Cash and deposits with central bank, Type: REAL)
[Question]
List securities codes and securities names with cash and deposits with central bank over the average.

Decompose the question into sub questions, considering [Requirements] and [SQL Constraints], and generate the SQL after thinking step by step:
[Answer]
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

[Schema]
{}
[Hint]
{}
[Question]
{}

Decompose the question into sub questions, considering [Requirements] and [SQL Constraints], and generate the SQL after thinking step by step:
[Answer]
"""

reviser_template = """
[Task]
You are an experienced financial database administrator.
When executing SQL below, some errors occurred, please fix up SQL and generate new SQL based on the information given.
Solve the task step by step if you need. When you find an answer, verify the answer carefully. 

[SQL Constraints]
When generating SQL, we should always consider constraints:
- In `SELECT <column>`, just select needed columns in the [Question] without any unnecessary column or value
- In `FROM <table>` or `JOIN <table>`, do not include unnecessary table
- If use max or min func, `JOIN <table>` FIRST, THEN use `SELECT MAX(<column>)` or `SELECT MIN(<column>)`
- If use `ORDER BY <column> ASC|DESC`, add `GROUP BY <column>` before to select distinct values

[Schema]
{}
[Hint]
{}
[Question]
{}
[old SQL]
```sql
{}
```
[SQLite error]
{}

Now please fix up old SQL and generate new SQL again.
The format of the new SQL is as follows.
```sql

```
[correct SQL]
"""
