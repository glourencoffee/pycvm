# Sobre

`cvm` é uma biblioteca Python cuja função é extrair os dados de companhias de capital
aberto fornecidos pela CVM, assim possibilitando o seu uso em sistemas automatizados.
A biblioteca foi projetada para fazer parte de um software para análise de companhias
abertas, embora ela possa ser utilizada por conta própria para outros fins.

# O que é a CVM?

CVM é a sigla para Comissão de Valores Mobiliários, que é o orgão governamental que
define os regulamentos para as companhias de capital aberto. Além de regular e
supervisionar tais companhias, a CVM também também disponibiliza os seus dados
para acesso público.

# Documentos da CVM

O [Portal de Dados da CVM][cvm-portal-de-dados-cia] disponibiliza os seguintes
tipos de documentos de companhias abertas:
- Formulário Cadastral (FCA)
- Demonstrações Financeiras Padronizadas (DFP)
- Informações Trimestrais (ITR)
- Formulário de Referência (FRE)
- Informes Periódicos e Eventuais (IPE)
- Informação Cadastral (CAD)

Atualmente, esta biblioteca apenas suporta os documentos FCA, DFP e ITR.

# Uso

```py
import cvm

for fca in cvm.csvio.fca_reader('caminho/para/arquivo/fca.zip'):
    print(fca.company_name, 'entregou o documento FCA em', fca.receipt_date)

for dfpitr in cvm.csvio.dfpitr_reader('caminho/para/arquivo/dfp_ou_itr.zip'):
    print(dfpitr.company_name, 'entregou o documento', dfpitr.type.name, 'em', dfpitr.receipt_date)
```

Note que a biblioteca não foi testada por completo e sua API ainda está instável.

  [cvm-portal-de-dados-cia]: <https://dados.cvm.gov.br/dataset/?groups=companhias>