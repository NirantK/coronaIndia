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
curl --header "Content-Type: application/json" --request POST --data '{"patients":[{"patientId":"1","notes":"Travelled from Italy"}]}' http://coronatravelhistory.pythonanywhere.com/
```

Python Example Request : 

```
import requests

headers = {
    'Content-Type': 'application/json',
}

data = '{
    "patients": [
        {
            "patientId": "1",
            "notes": "Indian Student Travelled from Italy, Family Member of P13 Friend with P12"
        }
    ]
}'

response = requests.post('http://coronatravelhistory.pythonanywhere.com/', headers=headers, data=data)

```
Input Data Example : 
```
{
    "patients": [
        {
            "patientId": "1",
            "notes": "Indian Student Travelled from Italy, Family Member of P13 Friend of P12"
        }
    ]
}
```
Returns : 
```
{
    "patients": [
        {
            "1": {
                "nationality": [
                    "Indian"
                ],
                "place_attributes": [
                    {
                        "is_foreign": true,
                        "place": "Italy"
                    }
                ],
                "relationship": [
                    {
                        "link": "Family Member",
                        "with": [
                            "P13"
                        ]
                    },
                    {
                        "link": "Friend",
                        "with": [
                            "P12"
                        ]
                    }
                ],
                "travel": [
                    "Italy"
                ]
            }
        }
    ]
}
```