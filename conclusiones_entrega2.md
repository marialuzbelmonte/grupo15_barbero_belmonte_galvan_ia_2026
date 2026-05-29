Nuestro código versus el de la IA:

La inteligencia artificial que utilizamos para resolver el punto 3 fue Gemini de Google, para la cual contamos con la versión paga. Al ejecutar el test sobre el código obtenido, el test cortó por timeout, mientras que el nuestro pasó todos los tests correctamente en 4,15 segundos.

Mirando el código, pudimos comprender que el problema del código presentado por Gemini consistía en usar cada celda de la cuadrícula como variable para decidir que colocar sobre ella. Esta solución resulataba muy lenta, ya que perdía tiempo calculando y combinando celdas vacías. Como vimos en clase, esto es incorrecto dado a que no todas las variables tendrán dominio y algunas quedarán vacías.

En cambio, en nuestra implementación, definimos como variables únicamente los múdulos reales que debíamos ubicar (hab, gen, etc...), dejando las coordenadas del mapa como el dominio. Al enfocarnos solo en los elementos importantes, reducimos las opciones posibles y el algoritmo logró completar el mapa en pocos segundos.

Esta estrategia nos permitió resolver varias reglas desde el inicio. Al definir los dominios de cada módulo, dejamos afuera los cráteres y filtramos de antemano que las esclusas vayan al borde y los dormitorios al interior. Esto nos ahorró procesar restricciones extra en medio de la ejecución, haciendo que el código sea mucho más limpio y rápido.

