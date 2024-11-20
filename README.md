# WeLang
WeLang — это простой интерпретируемый язык программирования, разработанный для ХАХАХАХА. Он поддерживает базовые операции с переменными, арифметические операции и выполнение команд. Ниже представлены основные возможности и команды, доступные в WeLang:

## Обзор команд
Объявление и присвоение переменных
```
var.create var_name
```
Описание: Объявляет новую переменную с именем var_name.
Пример:
```
var.create myVar
var.set var_name = 'значение'
```
Описание: Присваивает строковое 'значение' переменной var_name.
Пример:
```
var.set myVar = 'Привет мир'
```
## Арифметические операции
```
mov var_name, значение
```
Описание: Устанавливает целочисленное значение для var_name, перемещая значение в переменную.
Пример:
```
mov myVar, 10
add var_name, значение
```
Описание: Добавляет целое значение к текущему значению var_name.
Пример:
```
add myVar, 5 (Если myVar было 10, станет 15)
```
# Команды и выполнение
```
!set command = 'command_name'
```
Описание: Связывает ранее объявленную переменную с командой. Позволяет определить пользовательские команды на основе существующих переменных.
Пример: 
```
!set command = 'greet'
!cr var_name
```
Описание: Выполняет команду, связанную с var_name, обычно выводя значение переменной.
Пример: 
```
!cr myVar (Выводит значение myVar)
```
## Операции ввода/вывода
```
input var_name
```
Описание: Считывает ввод от пользователя и присваивает его переменной var_name.
Пример: 
```
input myVar ; Запрашивает у пользователя ввод значения для myVar
```
## Модификаторы

mod значение
Описание: Изменяет состояние модификаторов интерпретатора (например, включает или отключает режим отладки). Модификатор x023x используется для отключения режима отладки.
Пример:
```
mod debug или mod x023x
```
### Режим отладки
Интерпретатор имеет режим отладки, который выводит дополнительную информацию во время выполнения, например, объявления переменных и их присвоение. Вы можете включать или отключать его с помощью команды mod с соответствующим значением.

## Примеры
Пример 1: Объявление и использование переменной
```
var.create myVar
var.set myVar = 'Привет, WeLang!'
!cr myVar  ; Выводит: Привет, WeLang!
```
Пример 2: Арифметическая операция
```
var.create counter
mov counter, 10
add counter, 5
!cr counter  ; Выводит: 15
```
Пример 3: Использование ввода
```
var.create userInput
input userInput
!cr userInput  ; Выводит ввееденное значение
```
Пример 4: Выполнение пользовательской команды
```
var.create greet
var.set greet = 'Добро пожаловать в WeLang'
!set command = 'printGreeting'
!cr greet  ; Выводит: Добро пожаловать в WeLang
```

Заметили  недочет? Пишите в isuses!

