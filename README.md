# ISCpy

ISCpy is a robust ISC config file parser.
It reads and writes ISC-syled configuration files such as ISC BIND8/BIND9
and ISC-DHCP server/client files among a few others.
It has virtually unlimited possibilities for depth and quantity of these ISC config files.
ISC config files include BIND and DHCP config files.

## Usage

```
iscDictionary = ParseISCString(iscConfigString)
```
Returns the parsed ISC config file as a python dictionary in ISC dictionary format ( e.g. keys without childkeys or includes).


```
iscConfigString = MakeISC(iscDictionary)
```
Returns an ISC formatted file string which can be written back to the filesystem.

```
AddZone(json_zone, isc_dict)
```
Adds a zone to a parsed BIND config. Input is in JSON string. Returns ISC dictionary with added zone. This method doesn't include writing to an output file.

```
WriteToFile(iscDictionary, iscSpecialkeys, fullFilenameName)
```
Writes the ISC dictionary to the given file.
