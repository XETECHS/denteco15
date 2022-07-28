# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools.misc import formatLang, format_date

from num2words import num2words

LINE_FILLER = '*'


class PrintCheck(models.AbstractModel):
    _name = 'report.l10n_gt_check_printing.report_print_cheque'
    _description = 'Print Check'

    def get_date(self, date):
        if date:
            date = date.strftime("%Y-%m-%d")
            date = date.split('-')
            return date
        return ''

    def get_partner_name(self, obj, p_text):
        # if p_text and obj.partner_text:
        #     if p_text == 'prefix' :
        #         return obj.partner_text + ' ' + obj.partner_id.name
        #     else:
        #         return obj.partner_id.name + ' ' + obj.partner_text

        return obj.partner_id.name

    def amount_word(self, obj):
        language = 'es'
        amount_str = str('{:2f}'.format(obj.amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]

        before_amount_words = num2words(int(before_point_value), lang=language)

        amount = before_amount_words

        if obj.currency_id.currency_unit_label:
            amount = amount + ' ' + obj.currency_id.currency_unit_label

        if int(after_point_value) > 0:
            amount = amount + ' con ' + str(after_point_value) + '/100.'
        else:
            amount = amount + ' exactos.'

        # self.amount_in_words = amount.capitalize()

        first_line = amount.capitalize()

        if obj.cheque_formate_id.is_star_word:
            first_line = '***' + first_line + '***'

        first_line = first_line.replace(",", "")

        second_line = ""

        return [first_line, second_line]

        # amt_word = num2words(obj.amount)
        # lst = amt_word.split(' ')
        # lst.append(' only')
        # lst_len = len(lst)
        # first_line = ''
        # second_line = ''
        # for l in range(0, lst_len):
        #     if lst[l] != 'euro':
        #         if obj.cheque_formate_id.word_in_f_line >= l:
        #             if first_line:
        #                 first_line = first_line + ' ' + lst[l]
        #             else:
        #                 first_line = lst[l]
        #         else:
        #             if second_line:
        #                 second_line = second_line + ' ' + lst[l]
        #             else:
        #                 second_line = lst[l]
        #
        # if obj.cheque_formate_id.is_star_word:
        #     first_line = '***' + first_line
        #     if second_line:
        #         second_line += '***'
        #     else:
        #         first_line = first_line + '***'
        #
        # first_line = first_line.replace(",", "")
        # second_line = second_line.replace(",", "")
        #
        # return [first_line, second_line]

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.payment'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.payment',
            'docs': docs,
            #            'data': data,
            'get_date': self.get_date,
            'get_partner_name': self.get_partner_name,
            'amount_word': self.amount_word,
        }


class PrintChequeWizard(models.AbstractModel):
    _name = 'report.dev_print_cheque.cheque_report'
    _description = 'Print Cheque'

    def get_date(self, date):
        date = date.split('-')
        return date

    def amount_word(self, obj):
        self.ensure_one()

        language = 'en'

        list_lang = [['en', 'en_US'], ['en', 'en_AU'], ['en', 'en_GB'], ['en', 'en_IN'],
                     ['fr', 'fr_BE'], ['fr', 'fr_CA'], ['fr', 'fr_CH'], ['fr', 'fr_FR'],
                     ['es', 'es_ES'], ['es', 'es_AR'], ['es', 'es_BO'], ['es', 'es_CL'], ['es', 'es_CO'],
                     ['es', 'es_CR'], ['es', 'es_DO'],
                     ['es', 'es_EC'], ['es', 'es_GT'], ['es', 'es_MX'], ['es', 'es_PA'], ['es', 'es_PE'],
                     ['es', 'es_PY'], ['es', 'es_UY'], ['es', 'es_VE'],
                     ['lt', 'lt_LT'], ['lv', 'lv_LV'], ['no', 'nb_NO'], ['pl', 'pl_PL'], ['ru', 'ru_RU'],
                     ['dk', 'da_DK'], ['pt_BR', 'pt_BR'], ['de', 'de_DE'], ['de', 'de_CH'],
                     ['ar', 'ar_SY'], ['it', 'it_IT'], ['he', 'he_IL'], ['id', 'id_ID'], ['tr', 'tr_TR'],
                     ['nl', 'nl_NL'], ['nl', 'nl_BE'], ['uk', 'uk_UA'], ['sl', 'sl_SI'], ['vi_VN', 'vi_VN']]

        #     ['th','th_TH'],['cz','cs_CZ']

        cnt = 0
        for rec in list_lang[cnt:len(list_lang)]:
            if rec[1] == self.partner_id.lang:
                language = rec[0]
            cnt += 1

        amount_str = str('{:2f}'.format(self.amount_total))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]

        before_amount_words = num2words(int(before_point_value), lang=language)
        after_amount_words = num2words(int(after_point_value), lang=language)

        amount = before_amount_words

        if self.currency_id and self.currency_id.currency_unit_label:
            amount = amount + ' ' + self.currency_id.currency_unit_label

        if self.currency_id and self.currency_id.amount_separator:
            amount = amount + ' ' + self.currency_id.amount_separator

        if int(after_point_value) > 0:
            amount = amount + ' con ' + str(after_point_value) + '/100.'
        else:
            amount = amount + ' exactos.'

        # self.amount_in_words = amount.capitalize()

        first_line = amount.capitalize()

        if obj.cheque_formate_id.is_star_word:
            first_line = '***' + first_line + '***'

        first_line = first_line.replace(",", "")

        second_line = ""

        return [first_line, second_line]

        # amt = str(obj.amount)
        # amt_lst = amt.split('.')
        # amt_word = num2words(int(amt_lst[0]))
        # lst = amt_word.split(' ')
        # if float(amt_lst[1]) > 0:
        #     lst.append(' and ' + amt_lst[1] + '/' + str(100))
        # lst.append('only')
        # lst_len = len(lst)
        # lst_len = len(lst)
        # first_line = ''
        # second_line = ''
        # for l in range(0, lst_len):
        #     if lst[l] != 'euro':
        #         if obj.cheque_formate_id.word_in_f_line >= l:
        #             if first_line:
        #                 first_line = first_line + ' ' + lst[l]
        #             else:
        #                 first_line = lst[l]
        #         else:
        #             if second_line:
        #                 second_line = second_line + ' ' + lst[l]
        #             else:
        #                 second_line = lst[l]
        #
        # if obj.cheque_formate_id.is_star_word:
        #     first_line = '***' + first_line
        #     if second_line:
        #         second_line += '***'
        #     else:
        #         first_line = first_line + '***'
        #
        # first_line = first_line.replace(",", "")
        # second_line = second_line.replace(",", "")
        # return [first_line, second_line]

    def get_report_values(self, docids, data=None):
        docs = self.env['cheque.wizard'].browse(data['form'])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'cheque.wizard',
            'docs': docs,
            'get_date': self.get_date,
            'amount_word': self.amount_word,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
