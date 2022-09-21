# About

`cvm` is a Python library whose job is to extract data from publicly-held companies
provided by CVM, thus allowing its use in automated systems. The library was designed
to be part of a software for analysis of public companies, although it may be used on
its own for other purposes.

# What is the CVM?

CVM is the acronym for "Comissão de Valores Mobiliários" ("Securities and Exchange Commission"),
which is the government agency that defines the rules for publicly-held companies.
In addition to regulating such companies, CVM also makes their data available for
public access.

# CVM Documents

The [CVM's Data Portal][cvm-data-portal-co] provides the following types
of documents from publicly-held companies:
- Registration Form ("Formulário Cadastral" or "FCA")
- Standardized Financial Statements ("Demonstrações Financeiras Padronizadas" or "DFP")
- Quarterly Information ("Informações Trimestrais" or "ITR")
- Reference Form ("Formulário de Referência" or "FRE")
- Eventual and Periodical Reports ("Informes Periódicos e Eventuais" or "IPE")
- Registration Information ("Informação Cadastral" or "CAD")

Currently, this library only supports the documents FCA, DFP, and ITR.

# Usage

```py
import cvm

for fca in cvm.fca_reader('path/to/fca.zip'):
    print(fca.company_name, 'sent an FCA document on', fca.receipt_date)

for dfpitr in cvm.dfpitr_reader('path/to/dfp_or_itr.zip'):
    print(dfpitr.company_name, 'sent a', dfpitr.type.name, 'document on', dfpitr.receipt_date)
```

Note that this library has not been thoroughly tested and its API is still unstable.

More elaborated examples are in the directory `samples`:

```sh
> python -m samples.dfp.print_accounts 'path/to/dfp_or_itr.zip'
> python -m samples.dfp.print_balances 'path/to/dfp_or_itr.zip'
```

  [cvm-data-portal-co]: <https://dados.cvm.gov.br/dataset/?groups=companhias>