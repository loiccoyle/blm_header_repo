#!/usr/bin/env python3
import logging
import pandas as pd
from pathlib import Path
from blm_header import HeaderMaker
from blm_header.cli import file_name_to_file_stream
from blm_header.utils import DB, list_duplicates, sanitize_t


logging.getLogger('blm_header').setLevel(logging.INFO)

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

VEC_VAR = 'LHC.BLMI:LOSS_RS09'
DESTINATION_FOLDER = Path('headers_3')
HEADER_MAKER_KWARGS = {
        'look_forward': '120M',
        'look_back': '0M',
        'n_threads': 64,
        'n_jobs': -1,
        }
FILENAME = '{t}.csv'
HEADER_HEADER = []


def get_timber_meta():
    """Get the timestamps of changes in the vector numeric header form
    from timber's metadata.
    """
    meta = DB.getMetaData(VEC_VAR)[VEC_VAR]
    series = pd.Series(dict(zip(*meta)))
    series.index = pd.to_datetime(series.index, unit='s', utc=True)\
            .tz_convert('Europe/Zurich')
    return series

def get_closest_next_data(t, search_dt='30D', **kwargs):
    t = sanitize_t(t)
    fills = []
    t2 = t
    while fills == []:
        fills = DB.getLHCFillsByTime(t, t2, **kwargs)
        t2 += pd.Timedelta(search_dt)
        fills = [f for f in fills if len(f['beamModes']) < 20]
    return fills[0]


if __name__ == '__main__':
    LOGGER.info(f'Fetching timber meta timestamps.')
    # timber meta changes pd.Series, the index are the timestamps
    # the values are timber's BLM header
    timber_meta_changes = get_timber_meta()
    # keep timestamps after 2016
    timber_meta_changes = timber_meta_changes[timber_meta_changes.index > '2016-01-01 00:00:00']
    # get the list of timestamps
    timber_meta_timings = timber_meta_changes.index.tolist()
    # add a few by hand
    # timber_meta_timings += ['2018-01-01 00:00:00', '2018-04-10 00:00:00']
    timber_meta_timings = ['2018-01-01 00:00:00', '2018-04-10 00:00:00']
    msg = "Makings headers for:\n\t" + '\n\t'.join(map(str, timber_meta_timings))
    LOGGER.info(msg)

    # generate the headers
    for t in timber_meta_timings:
        # reset header's header
        HEADER_HEADER = []
        # make sure there is data to match on to not just match on noise...
        fill = get_closest_next_data(t, beam_modes=['STABLE'], unixtime=True)
        LOGGER.info(f'Found next fill for matching: {fill["fillNumber"]}.')
        msg = '\n\t'.join([f'{b["mode"]}: {sanitize_t(b["startTime"])} -> {sanitize_t(b["endTime"])}'
                           for b in fill['beamModes']])
        LOGGER.info(f'Fill info:\n\t' + msg)
        t_data = [b for b in fill['beamModes'] if b['mode'] == 'INJPROT'][0]
        # set requested time to the start of INJPROT
        t_data = t_data['startTime']
        # make the header
        hm = HeaderMaker(t_data, **HEADER_MAKER_KWARGS)
        try:
            header = hm.make_header()
        except ValueError as e:
            LOGGER.warning(e)

        # the header's header ...
        HEADER_HEADER.append(f'# Requested time: "{t}"')
        HEADER_HEADER.append(f'# Time range used for matching: "{hm.t1}" -> "{hm.t2}"')
        HEADER_HEADER.append(f'# Fill number: {fill["fillNumber"]}')
        HEADER_HEADER.append(f'# Settings used: {HEADER_MAKER_KWARGS}')

        # check for duplicates
        if len(set(header)) != len(header):
            msg = ('There are duplicates in the header !'
                   ' Consider increasing the look back/forward amounts.')
            HEADER_HEADER.append('# ' + msg)
            LOGGER.warning(msg)
            for blm, dupe_indices in list_duplicates(header):
                msg = f'BLM "{blm}" appears {len(dupe_indices)} times at indices {dupe_indices}'
                HEADER_HEADER.append('# ' + msg)
                LOGGER.warning(msg)

        # Save to file
        file_name_to_file_stream(str(DESTINATION_FOLDER / FILENAME), sanitize_t(t))\
                .write('\n'.join(HEADER_HEADER + header))

