# Sobre

`cvm` é uma biblioteca Python cuja função é extrair os dados de companhias de capital
aberto fornecidos pela CVM, assim possibilitando o seu uso em sistemas automatizados.
A biblioteca foi projetada para fazer parte de um software para análise de companhias
abertas, embora ela possa ser utilizada por conta própria para outros fins.

# O que é a CVM?

CVM é a sigla para Comissão de Valores Mobiliários, que é o orgão governamental que
define os regulamentos para as companhias de capital aberto. Além de regular e
supervisionar tais companhias, a CVM também disponibiliza os seus dados para
acesso público.

# Documentos da CVM

O [Portal de Dados da CVM][cvm-portal-de-dados-cia] disponibiliza os seguintes
tipos de documentos de companhias abertas:
- Formulário Cadastral (FCA)
- Demonstrações Financeiras Padronizadas (DFP)
- Informações Trimestrais (ITR)
- Formulário de Referência (FRE)
- Informes Periódicos e Eventuais (IPE)
- Informação Cadastral (CAD)

Atualmente, esta biblioteca suporta os documentos FCA, FRE (parcial), DFP e ITR.

# Uso

```py
import cvm

with cvm.FCAFile('caminho/para/fca.zip') as file:
    for fca in file:
        print(fca.company_name, 'entregou o documento FCA em', fca.receipt_date)

with cvm.DFPITRFile('caminho/para/dfp_ou_itr.zip') as file:
    for dfpitr in file:
        print(dfpitr.company_name, 'entregou o documento', dfpitr.type.name, 'em', dfpitr.receipt_date)
```

Note que a biblioteca não foi testada por completo e sua API ainda está instável.

Exemplos mais elaborados de uso estão no diretório `samples`:

```sh
> python -m samples.dfp.print_accounts 'caminho/para/dfp_ou_itr.zip'
> python -m samples.dfp.print_balances 'caminho/para/dfp_ou_itr.zip'
```

  [cvm-portal-de-dados-cia]: <https://dados.cvm.gov.br/dataset/?groups=companhias>