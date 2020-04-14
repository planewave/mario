import json

if __name__ == "__main__":
    file_name = 'foo.json'
    data = {
        'info': {
            'version': 0.1,
            'description': 'a test verison of spectrum labels',
            'contributor': 'xiao'
        },
        'captures': [
            {
                'file_name': 'my_device_2020_02_25_11_56_36.dat',
                'fs': 56e6,
                'fc': 0.0,
                'sdr': 'usrp',
                'annotation': [
                    {
                        'fc_off': 1e6,
                        'bw': 10e6,
                        'device': 'mavic2_dr'
                    },
                    {
                        'fc_off': -3e6,
                        'bw': 9e6,
                        'device': 'p4p_dr'
                    }
                ]
            }
        ]
    }

    with open(file_name, 'w') as f:
        json.dump(data, f)
