# Distribuir las imágenes Docker por USB (descargar una vez, cargar en todos)

Descargar ~5 GB en 15 puestos a la vez satura cualquier red de aula. El patrón:

## En el PRIMER puesto (ya provisionado y verificado)
```bash
cd curso-bigdata-ia
docker compose pull            # descarga jupyter + namenode + datanode
docker save \
  quay.io/jupyter/pyspark-notebook:latest \
  bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8 \
  bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8 \
  -o imagenes-curso.tar        # ~5-6 GB: cópialo a un USB
```

## En CADA uno de los demás puestos
```bash
docker load -i /ruta/al/usb/imagenes-curso.tar
cd curso-bigdata-ia && docker compose up -d    # arranca sin descargar nada
```

Nota: el USB debe ir formateado en exFAT o ext4 (FAT32 no admite ficheros >4 GB).
