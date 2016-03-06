item_db = {
    "pebble": {
        "description": "A pebble",
        "examination": "A pebble. It is rather smooth.",
        "actions": {
            "throw": lambda args: print("Threw rock"),
            "flirt": lambda args: print("The pebble is indifferent.")
        },
        "weight": 0.01
    },
    "log": {
    	"description": "A log",
    	"examination": "",
    	"actions": {
    		"flirt": lambda args: print("The log appears to stiffen.")
    	},
    	"weight": 500
    }
}