calls = {
    "PING": ('utils', 'PingRequest'),
	"LOGIN": ('auth', 'LoginRequest'),
    "PRICECHECK": ('trade', 'PriceCheckRequest'),
    "QTYCHECK": ('trade', 'QtyCheckRequest'),
    "LISTQUALITIES": ('trade', 'ListQualitiesRequest'),
    "LISTTYPES": ('trade', 'ListTypesRequest'),
    #"LISTPRODUCTS": ('trade', 'ListProductsRequest'),
    "TRANSACT": ('trade', 'TransactRequest'),
    "TRANSACTINFO": ('trade', 'TransactInfoRequest'),
    "TRANSACTCANCEL": ('trade', 'TransactCancelRequest'),
    "PAY": ('trade', 'PayRequest'),
}
