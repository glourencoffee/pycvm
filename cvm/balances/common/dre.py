import typing
from cvm import balances

class CommonDREValidator(balances.AccountLayoutValidator):
    def _prepare(self):
        self._da = None
        self._da_found_count = 0

    def _process(self, code: str, name: str, quantity: int, is_fixed: bool):
        if self._da_found_count == 2:
            return

        ################################################################################
        # Check if this is an amortization or depreciation account.
        #
        # Amortization and depreciation accounts are non-fixed. That means they are not
        # predefined but rather chosen by whoever sent the company's data using the ENET
        # software. However, since the chosen name must make sense to the person who's
        # reading the data (the investor or else), we can check for sensible names. Here
        # are some examples of chosen names:
        # - Depreciação e Amortização
        # - Depreciação e Amortizacão
        # - Depreciações e Amortização
        # - Depreciação/Amortização
        #
        # Moreover, some companies discriminate their depreciation and amortization into
        # two accounts, while others keep it in only one:
        # - Depreciação
        # - Amortização
        # 
        # That's what the counter is for: in case there's more than one account, their
        # quantities are summed up into a single D&A variable.
        # 
        # Now, regarding the account's name, by checking for lowercase 'deprecia' and/or
        # 'amortiza', we cover pretty much all cases.
        ################################################################################
        lcname       = name.lower()
        has_deprecia = 'deprecia' in lcname
        has_amortiza = 'amortiza' in lcname

        if has_deprecia and has_amortiza:
            self._da = quantity
            self._da_found_count = 2
            
        elif has_deprecia or has_amortiza:
            self._da_found_count += 1

            if self._da_found_count == 1:
                self._da = quantity
            else:
                self._da += quantity

    def _finish(self, attributes: typing.Dict[str, int]):
        operating_income_and_expenses = attributes['operating_income_and_expenses']

        if self._da is None:
            operating_result = None
        else:
            # EBITDA = EBIT + DA
            operating_result = attributes['operating_profit'] + abs(self._da)
            operating_income_and_expenses += abs(self._da)
        
        attributes['depreciation_and_amortization'] = self._da
        attributes['operating_income_and_expenses'] = operating_income_and_expenses
        attributes['operating_result']              = operating_result