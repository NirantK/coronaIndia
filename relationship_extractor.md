# What works for relationship extraction API

## Relationship 
What works

```
"Family of P13"
"Son of P12 and Daughter of P12"
"Friend of P12, P12, 14 and son of P13"
```

What doesn't work : Relationship without word `of`
```
"Friend: P12"
"Friends with P12"
"Wife of p12" #Expected P12 (throws error with small p)
```

## Travel Places
What works
```
Travelled from Wuhan
Travel history Italy, Pune, Mumbai
Travlled from South Korea via Mumbai
```

## Nationality 
What works 
```
Indian student studying in wuhan
Italian tourise
```
What doesn't work
```
Indian travelling with Italian tourist
# Will return Indian and Italian
```

## API Details 
API URL : http://coronatravelhistory.pythonanywhere.com/

Example request :
```
curl --header "Content-Type: application/json" --request POST --data '{"patients":[{"patientId":"1","notes":"Student from Wuhan, recovery confirmed on 14 Feb"},{"patientId":"2","notes":"Family members of P4"},{"patientId":"3","notes":"Travel from Italy on 29/02/2020 through Doha"}]}' http://coronatravelhistory.pythonanywhere.com/
```

Python Example Request : 

```
import requests

headers = {
    'Content-Type': 'application/json',
}

data = '{"patients":[{"patientId":"1","notes":"Student from Wuhan, recovery confirmed on 14 Feb"},{"patientId":"2","notes":"Family members of P4"},{"patientId":"3","notes":"Travel from Italy on 29/02/2020 through Doha"}]}'

response = requests.post('http://coronatravelhistory.pythonanywhere.com/', headers=headers, data=data)

```
Input Data Example : 
```
{
   "patients":[
      {
         "patientId":"1",
         "notes":"Student from Wuhan, recovery confirmed on 14 Feb"
      },
      {
         "patientId":"2",
         "notes":"Family members of P4 and Friend with P2"
      },
      {
         "patientId":"3",
         "notes":"Travel from Italy on 29/02/2020 through Doha"
      }
   ]
}
```
Returns : 
```
{
   "patients":[
      {
         "1":{
            "nationality":[

            ],
            "relationship":[],
            "travel":[
               "Wuhan"
            ]
         }
      },
      {
         "2":{
            "nationality":[

            ],
            "relationship":[{"link": "Family Member", "with": "P4"}, {"link" : "Friend", "with": P2}],
            "travel":[

            ]
         }
      },
      {
         "3":{
            "nationality":[

            ],
            "relationship":[],
            "travel":[
               "Italy",
               "Doha"
            ]
         }
      }
   ]
}
```