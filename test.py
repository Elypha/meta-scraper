videoc
bskc001
html_dmm_c0, dmm_type = get_dmm('bskc001')
lx = html.fromstring(html_dmm_c0.text)

videoa
ssis00279
html_dmm_a0, dmm_type = get_dmm('ssis00279')
lx = html.fromstring(html_dmm_a0.text)

dvd
h_1133teng006
html_dmm_d0, dmm_type = get_dmm('h_1133teng006')
lx = html.fromstring(html_dmm_d0.text)




MGS

ABW-254
html_mgs = JK.web.get(F'https://www.mgstage.com/product/product_detail/ABW-254/', cookies={'adc': '1', 'mgs_agef': '1'})
lx_mgs_d0 = html.fromstring(html_mgs.text)
lx = lx_mgs_d0

348NTR-044
html_mgs = JK.web.get(F'https://www.mgstage.com/product/product_detail/348NTR-044/', cookies={'adc': '1', 'mgs_agef': '1'})
lx_mgs_h0 = html.fromstring(html_mgs.text)
lx = lx_mgs_h0
