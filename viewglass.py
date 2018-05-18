"""Usage: viewglass.py -z zipcode [-o output_file] [-q]

Options:
-h --help    show this
-z zipcode   the zip code for which intelligence has to run
-o FILE      specify output file [default: ./test.txt]
-q           do not log api responses
"""
import signal
import datetime
import sys
import requests
import time
import threading
from docopt import docopt
from datetime import datetime as dt


def utc2local(utc):
    epoch = time.mktime(utc.timetuple())
    offset = dt.fromtimestamp(epoch) - dt.utcfromtimestamp(epoch)
    return utc + offset


def getWeatherData(zipcode):
    url = 'http://api.openweathermap.org/data/2.5/weather?zip={},us&APPID=3cf4cd87d12e4025c0636ed5097aef1e&units=imperial'.format(zipcode)
    r = requests.get(url)
    return r.json()


class Intelligence(threading.Thread):
    def __init__(self, out_file, zipcode, quiet):
        threading.Thread.__init__(self)
        self.zipcode = zipcode
        self.out_file = out_file
        self.quiet = quiet
        self.f = open(self.out_file, "w")
        self.iter = True
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.iter = False
        print("Process being terminated \n")
        if self.f is not None:
            print("Closing output file handle: {}\n".format(self.out_file))
            self.f.close()
        sys.exit(0)

    def run(self):
        try:
            while self.iter:
                response = getWeatherData(self.zipcode)
                cloud = response['clouds']['all']
                temp = response['main']['temp']
                sunrise = datetime.datetime.fromtimestamp(response['sys']['sunrise'])
                sunset = datetime.datetime.fromtimestamp(response['sys']['sunset'])
                visibility = response['visibility']
                currentTime = datetime.datetime.now()
                if not self.quiet:
                    self.f.write("Current time : {} \n".format(str(((currentTime)).time())))
                    self.f.write("Temp : {} \n".format(str(temp)))
                    self.f.write("Sunrise : {} \n".format(str(sunrise)))
                    self.f.write("Sunset : {} \n".format(str(sunset)))
                selectedTint = 1
                if (currentTime.time().hour < sunrise.hour or currentTime.time().hour > sunset.hour):
                    selectedTint = 1
                elif cloud > 40 or visibility < 3000:
                    selectedTint = 2
                elif cloud < 40 or visibility > 3000:
                    if temp > 80:
                        selectedTint = 4
                    elif temp > 65:
                        selectedTint = 3
                    else:
                        selectedTint = 2
                msg = "Selected Tint : {}\n".format(selectedTint)
                self.f.write(msg)
                print (msg)
                time.sleep(2)
        except KeyError:
            self.iter = False
            print("I got a KeyError - reason '%s'" % str(response.get('message')))
        except requests.exceptions.ConnectionError:
            msg = "Connection issue. Trying again ...\n"
            print (msg)
            self.f.write(msg)
            time.sleep(2)
            self.run()

if __name__ == "__main__":
    arguments = docopt(__doc__, version='Intelligence QA 1.0')
    out_file = arguments.get('-o', 'test.txt')
    zipcode = arguments.get('-z')
    quiet = arguments.get('-q', False)
    intelligence = Intelligence(out_file, zipcode, quiet)
    intelligence.start()
    intelligence.join()
