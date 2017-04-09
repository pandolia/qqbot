# (1) test list
- http://127.0.0.1:8188/list/buddy
- http://127.0.0.1:8188/list/buddy/Eva
- http://127.0.0.1:8188/list/buddy/x
- http://127.0.0.1:8188/list/x
- http://127.0.0.1:8188/list/buddy/xx/xx

- http://127.0.0.1:8188/list/group
- http://127.0.0.1:8188/list/group/connie
- http://127.0.0.1:8188/list/group/x

- http://127.0.0.1:8188/list/discuss
- http://127.0.0.1:8188/list/discuss/MyDiscuss
- http://127.0.0.1:8188/list/discuss/x

- http://127.0.0.1:8188/list/group-member/connie
- http://127.0.0.1:8188/list/group-member/connie/Eva
- http://127.0.0.1:8188/list/group-member/connie/158297369
- http://127.0.0.1:8188/list/group-member/x
- http://127.0.0.1:8188/list/group-member/connie/x

- http://127.0.0.1:8188/list/discuss-member/MyDiscuss
- http://127.0.0.1:8188/list/discuss-member/MyDiscuss/Eva
- http://127.0.0.1:8188/list/discuss-member/MyDiscuss/158297369
- http://127.0.0.1:8188/list/discuss-member/x
- http://127.0.0.1:8188/list/discuss-member/MyDiscuss/x

# (2) test send
- http://127.0.0.1:8188/send/buddy/Eva/nihao%20%E4%BD%A0%E5%A5%BD%20wohao
- http://127.0.0.1:8188/send/buddy/hcj
- http://127.0.0.1:8188/send/buddy/qwe323/fdsf

- http://127.0.0.1:8188/send/group/connie/wohao%20%E6%88%91%E5%A5%BD%20wohao
- http://127.0.0.1:8188/send/group/connie
- http://127.0.0.1:8188/send/group/qwe323/fdsf

- http://127.0.0.1:8188/send/discuss/MyDiscuss/tahao%20%E4%BB%96%E5%A5%BD%20tahao
- http://127.0.0.1:8188/send/discuss/MyDiscuss
- http://127.0.0.1:8188/send/discuss/qwe323/fdsf

# (3) test group-manager
- http://127.0.0.1:8188/group-set-admin/connie/158297369%2C3497303033
- http://127.0.0.1:8188/group-unset-admin/connie/158297369%2C3497303033

- http://127.0.0.1:8188/group-unset-admin/connie/sdds%2Cdsad
- http://127.0.0.1:8188/group-unset-admin/connie/sdds%2Cdsad/cxzc
- http://127.0.0.1:8188/group-unset-admin/connie

- http://127.0.0.1:8188/group-set-card/connie/158297369%2C3497303033/card
- http://127.0.0.1:8188/list/group-member/connie
- http://127.0.0.1:8188/list/group-member/connie/card

- http://127.0.0.1:8188/group-unset-card/connie/card
- http://127.0.0.1:8188/list/group-member/connie
- http://127.0.0.1:8188/list/group-member/connie/card

- http://127.0.0.1:8188/group-shut/connie/158297369%2C3497303033

- http://127.0.0.1:8188/group-kick/connie/158297369%2C3497303033

# (4) test plugin
- http://127.0.0.1:8188/plugins
- http://127.0.0.1:8188/plug/sample
- http://127.0.0.1:8188/plug/sched
- http://127.0.0.1:8188/plugins
- http://127.0.0.1:8188/unplug/sample
- http://127.0.0.1:8188/unplug/sched
- http://127.0.0.1:8188/plugins

# (5) test help
- http://127.0.0.1:8188/help
