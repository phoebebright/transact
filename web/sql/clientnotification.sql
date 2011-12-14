
INSERT INTO `web_clientnotification` 
VALUES 
('1', 'TransactionPaid', '', 'Payment Received at TransAct Carbon', 'Your payment for transaction id {{trans.uuid}} has been processed.\r\n\r\nPurchase of {{trans.quantity}} tonnes of {{product.name}} for {{trans.total}}.\r\n\r\nThank you.\r\n', 'info@transactcarbon.com', '0'), 
('2', 'AccountRecharge', '', 'Your account at TransactCarbon has been Recharged', 'Your account has been recharged as it fell below the minimum level of {{client.recharge_level}}.\r\n\r\nYour new account balance is {{client.currency}} {{client.balance}}\r\n', 'info@transactcarbon.com', '0');
