# -*- coding: utf-8 -*-

from datetime import timedelta
from datetime import datetime
import os
from time import time, localtime, strftime
from numpy import float64,float32,int32,uint16,int16,uint8, nan

from pyscada import log
from pyscada.models import Variable
from pyscada.models import RecordedDataFloat
from pyscada.models import RecordedDataInt
from pyscada.models import RecordedDataBoolean
from pyscada.models import InputConfig
from pyscada.models import RecordedTime
from pyscada.export.hdf5 import mat

"""
export measurements from the database to a file
"""


def timestamp_unix_to_matlab(timestamp):
    return (timestamp/86400)+719529

def export_database_to_mat(filename=None,time_id_min=None,time_id_max=None):
    
    if filename is None:
        backup_file_path = os.path.expanduser('~/measurement_data_dumps')
        backup_file_name = 'measurement_data'
        if not os.path.exists(backup_file_path ):
            os.mkdir(backup_file_path)
        cdstr = strftime("%Y_%m_%d_%H%M",localtime())
        filename = os.path.join(backup_file_path,backup_file_name + '_' + cdstr + '.mat')
    
    last_time_id = RecordedTime.objects.last().pk
    first_time_id = RecordedTime.objects.first().pk
    if time_id_max is not None:
        last_time_id = min(last_time_id,time_id_max)
    
    if time_id_min is not None:
        first_time_id = max(first_time_id,time_id_min)


    timevalues = [timestamp_unix_to_matlab(element) for element in RecordedTime.objects.filter(id__lte=last_time_id, id__gte=first_time_id).values_list('timestamp',flat=True)]
    time_ids = list(RecordedTime.objects.filter(id__lte=last_time_id, id__gte=first_time_id).values_list('id',flat=True))
    
    bf = mat(filename)
    bf.write_data('time',float64(timevalues))
    

    for val in Variable.objects.all():
        variable_class = InputConfig.objects.get_value_by_key('class',variable_id=val.pk).replace(' ','')
        if variable_class.upper() in ['FLOAT32','SINGLE','FLOAT','FLOAT64','REAL'] :
            r_time_ids = list(RecordedDataFloat.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time_id',flat=True))
            r_values = list(RecordedDataFloat.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('value',flat=True))
        elif variable_class.upper() in ['INT32','UINT32','INT16','INT','WORD','UINT','UINT16']:
            r_time_ids = list(RecordedDataInt.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time_id',flat=True))
            r_values = list(RecordedDataInt.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('value',flat=True))
        elif variable_class.upper() in ['BOOL']:
            r_time_ids = list(RecordedDataBoolean.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('time_id',flat=True))
            r_values = list(RecordedDataBoolean.objects.filter(variable_id=val.pk,time_id__lte=last_time_id, time_id__gte=first_time_id).values_list('value',flat=True))
        
        
        tmp = [0]*len(time_ids)
        t_idx = 0
        v_idx = 0
        nb_v_idx = len(r_time_ids)-1
        for id in time_ids:
            if nb_v_idx < v_idx: 
                if t_idx > 0:
                    tmp[t_idx] = tmp[t_idx-1]
            else:
                if r_time_ids[v_idx]==id:
                    tmp[t_idx] = r_values[v_idx]
                    laid = id
                    v_idx += 1
                elif t_idx > 0:
                    tmp[t_idx] = tmp[t_idx-1]

                if nb_v_idx > v_idx:
                    while r_time_ids[v_idx]<=id and v_idx <= nb_v_idx:
                        log.debug(("double id %d ")%(id))
                        v_idx += 1
            t_idx += 1
                
        if variable_class.upper() in ['FLOAT','FLOAT64','DOUBLE'] :
            tmp = float64(tmp)
        elif variable_class.upper() in ['FLOAT32','SINGLE','REAL'] :
            tmp = float32(tmp)
        elif  variable_class.upper() in ['INT32']:
            tmp = int32(tmp)
        elif  variable_class.upper() in ['WORD','UINT','UINT16']:
            tmp = uint16(tmp)    
        elif  variable_class.upper() in ['INT16','INT']:
            tmp = int16(tmp)
        elif variable_class.upper() in ['BOOL']:
            tmp = uint8(tmp)
        else:
            tmp = float64(tmp)
        
        bf.write_data(val.variable_name,tmp)
        bf.reopen()
    
    bf.close_file()

