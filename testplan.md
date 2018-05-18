# Test plan for module viewglass.py
## Functional tests:

1. Usage:
	* check that we can run script with only -z parameter and -q and -o will have default value False and test.txt accordingly 
		```bash
        python viewglass.py -z 95125
        ```

	* check that we can specify that output file with -o 'filename' , and appropriate file will be created with the same name
	    ```bash
		python viewglass.py -z 95125 -o file1.txt
        ```

	* check that script will show the usage without parameters:
		```bash
        python viewglass.py
		Usage: viewglass.py -z zipcode [-o output_file] [-q]
		```
	* check that script will show the usage with wrong parameters:
		```bash
		python viewglass.py -z 95125 -i
		Usage: viewglass.py -z zipcode [-o output_file] [-q]
		```
2. Zipcode
	* check valid zipcode , and make sure that script is running and file populating with information
		```bash
		python viewglass.py -z 95125 -o file1.txt
		```
	* check invalid zipcode and make sure that script will show "I got a KeyError" message
		
        not valid zipcodes: kdasj, 988888, +/-09, etc.
		```bash
        python viewglass.py -z 9512
		I got a KeyError - reason 'city not found'
        ```

	* check empty zipcode and make sure that Usage message appeared:
		```bash
        python viewglass.py -z
		-z requires argument
		Usage: viewglass.py -z zipcode [-o output_file] [-q]
		```
3. File
	* run script with -q option and check that file created with appropriate name and have only 'Selected Tint' information.
		```bash
		python viewglass.py -z 95125 -o filename -q
		cat filename
			Selected Tint : 3
 			Selected Tint : 3
 			Selected Tint : 3
         ```

	* run script without -q option and check that file created with appropriate name and have information about 
	Current time,Temp, Sunrise, Sunset and Selected Tint for each iteration
		```bash
		python viewglass.py -z 95125 -o filename
        
		cat filename
		```
        
        ```
        Temp : 65.97 
		Sunrise : 2018-05-17 05:56:23 
		Sunset : 2018-05-17 20:11:56 
 		Selected Tint : 3
        ````


4. Tint:
	* night time test.
		Test that tint will 1 in the nighttime (before sunrise.hour and after sunset.hour) for several zip codes : 95125, 10009
		change current time to 00:00:00 midnight (using decorator freeze_time fo example, mock doesn't work with datetime.now())
		check that selected tint always 1

	* daytime test with cloud > 40 or visibility < 3000.
		mock api response and change weather conditions.
		Test that tint in this case will be 2.

	* daytime test with cloud < 40 or visibility > 3000 and temp > 80.
		mock api response and change weather conditions.
		Test that tint in this case will be 4.
		
	* daytime test with cloud < 40 or visibility > 3000 (temp > 65 and temp < 80)
		mock api response and change weather conditions.
		Test that tint in this case will be 3.
		
	* daytime test with cloud < 40 or visibility > 3000 (temp < 65)
		mock api response and change weather conditions.
		Test that tint in this case will be 2.
		
5. Connection error:
	* check that after loosing connection , script will trying to reconnect.

	* check that if there is no connection and connection appears after sometime, script will reconnect.


