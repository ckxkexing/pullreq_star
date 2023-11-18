
### manual feature

```sh
# setting In `config/feature_configs.yaml`
python -m src.main -c config/feature_configs.yaml -o features
```

### diff input 

```sh
python -m src.main_diff
```

### description input

```sh
python -m src.main_description
```

### label state
```sh
python -m src.main -c config/label_state_configs.yaml -o label_state
```

### insert/export data
```sh
python tools/export_features.py
```

### Thanks
- Gousios
- Xunhui Zhang
- Myself
