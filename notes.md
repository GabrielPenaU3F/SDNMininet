# Comandos de Linux para trabajar con Mininet

## Construir red con topología simple

```bash
sudo mn
```

## Borrar todas las redes y limpiar todo

```bash
sudo mn -c
```

## Construir una topología con tres hosts y un switch
```bash
sudo mn --topo single,3
```

## Construir una topología lineal (cadena de switches)
```bash
sudo mn --topo linear,3
```

## Construir una topología tipo árbol
```bash
sudo mn --topo tree,depth=2,fanout=2
```

## Levantar una topología preconstruida
```bash
sudo mn --custom mi_topo.py --topo mitopo
```

## Levantar con un controlador específico
```bash
sudo mn --custom topo.py --topo mitopo --controller=remote
```


# Comandos de Mininet

## Pinguear a todos los hosts

```bash
pingall
```

## Pinguear indefinidamente a un host

```bash
h1 ping h2
```

## Pinguear un número fijo de paquetes
h1 ping -c 4 h2

## Abrir terminales para hosts específicos
gterm h1 h8

## Correr archivo Python en un host
h1 python3 path/archivo.py args

## Correr un script en la terminal principal de Mininet
source archivo.mn

# Comandos Ryu

## Switch básico

```bash
ryu-manager ryu.app.simple_switch_13
```