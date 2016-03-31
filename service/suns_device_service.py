#!/usr/bin/env python

"""
  Copyright (c) 2014, SunSpec Alliance
  All Rights Reserved

"""

import sys
import time
import sunspec.core.client as client
import sunspec.core.suns as suns
import cherrypy
import traceback
import json


class SunsDeviceService(object):

    @cherrypy.expose
    def device(self, ifc='tcp', ipaddr='127.0.0.1', ipport=502, slaveid= 1, timeout=5, name=None, baudrate=9600, parity='N'):
        # return '{"status": "SUCCESS", "result": "device output - ipaddr = %s  ipport = %d  timeout = %d"}' % (ipaddr, ipport, timeout)
        # required because cherrypi casts to string
        ipport = int(ipport)
        slaveid = int(slaveid)
        timeout = int(timeout)
        status = 'SUCCESS'
        status_detail = ''
        result = ''
        jsonResult = ''
        try:
            if ifc == 'tcp':
                status_detail += 'IP Address: %s, IP Port: %d, Slave Id: %d, Timeout: %d, ' % (ipaddr, int(ipport), int(slaveid), int(timeout))
                sd = client.SunSpecClientDevice(client.TCP, slaveid, ipaddr=ipaddr, ipport=ipport, timeout=timeout)
            elif ifc == 'rtu':
                sd = client.SunSpecClientDevice(client.RTU, slaveid, name=name, baudrate=baudrate, timeout=timeout)
            elif ifc == 'mapped':
                sd = client.SunSpecClientDevice(client.MAPPED, slaveid, name=name)
            else:
                raise Exception('Invalid ifc param type: %s' % ifc)

            status_detail += 'Timestamp: %s' % (time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))

            if sd is not None:
                # read all models in the device
                sd.read()
                print 'this is the next item'
                print str(dir(sd.device.models_list[0]))
                asdf = sd.device.models_list
                #jsonResult = json.dumps( sd )
                #cherrypi.log(jsonResult)

                # NB: the following loop is not actually used - we return 'sd' to the client, & they sort it themselves
                # One day, I hope to be able to get json serialization working!
                for model in sd.device.models_list:
                    label = '(%s)' % (str(model.id))
                    result += '{"model":'
                    result += '{"name":"%s",' % (label)
                    result += '"value":"'
                    for block in model.blocks:
                        if block.index > 0:
                            index = '%02d-' % (block.index)
                        else:
                            index = '   '
                        for point in block.points_list:
                            if point.value is not None:
                                if point.point_type.label:
                                    label = '   %s%s (%s)-' % (index, point.point_type.label, point.point_type.id)
                                else:
                                    label = '   %s(%s)-' % (index, point.point_type.id)
                                units = point.point_type.units
                                if units is None:
                                    units = ''
                                if point.point_type.type == suns.SUNS_TYPE_BITFIELD16:
                                    value = '0x%04x' % (point.value)
                                elif point.point_type.type == suns.SUNS_TYPE_BITFIELD32:
                                    value = '0x%08x' % (point.value)
                                else:
                                    value = str(point.value).rstrip('\0')
                                result += '%-20s %10s %-10s' % (label, value, str(units))
                    result += '"},'
                result += '"}'

        except Exception, e:
            traceback.print_exc()
            status = 'FAILURE'
            status_detail = str(e)

        resp = '{"status":"%s"' % status
        if status_detail:
            resp += ',"statusDetail": "%s"' % status_detail
        resp += '}'
        if result:
            resp += ',"result": %s' % sd

        return resp

service = SunsDeviceService()

if __name__ == "__main__":
    cherrypy.quickstart(service)

