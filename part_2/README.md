# DebtSimplifer

## Algorytm

### Wstęp

Do rozwiązania problemu optymalizacji płatności między znajomymi użyłem programowania całkowitoliczbowego.

Problem ten, możemy widzieć jako instancję ILP. Najpierw, przed uruchomieniem algorytmu, liczymy ile dany dłużnik jest winny, a ile zwrotu powinien dostać każdy z wierzycieli. Niech $D$ to zbiór dłużników, $W$ to zbiór wierzycieli, $a_d$ to dług dłużnika $d$, a $b_w$ to świadczenia wierzyciela $w$. 

### Zmienne

Problem ma dwa rodzaje zmiennych:

- $0 \leq x_{dw} \leq a_i$ - ile dłużnik $d$ płaci wierzycielowi $w$
- $y_{dw} \in \{0,1\}$ - czy dłużnik $d$ płaci wierzycielowi $w$

### Ograniczenia

Każdy z dłużników powinien w sumie zapłacić tyle, ile ma długu:

$$(\forall d \in D)\left( \sum_{w\in W} x_{dw} = a_{d} \right)$$

Każdy z wierzycieli powininen dostać w sumie tyle, ile wynoszą jego świadczenia:

$$(\forall w \in W)\left( \sum_{d\in D} x_{dw} = b_{w} \right)$$

Jeżeli $x_{dw}>0$ to $y_{dw}=1$, w przeciwnym przypadku $y_{dw}=0$. Możemy zapisać to jako nierówność (nie zajdzie nigdy $x_{dw} > 0$ i $y_{dw} = 0$):

$$ x_{dw} \leq y_{dw} \cdot a_d $$

### Cel optymalizacyjny

Chcemy zminimalizować liczbę transakcji, a więc sumę po zmiennych $y_{dw}$:
$$\sum_{d\in D, w\in W}  y_{dw}  \to \min$$

### Technologia

Użyłem biblioteki `pulp 2.8.0`, która używa solvera typu CBC.

### Podsumowanie algorytmu

Algorytm zwraca optymalny wynik dla każdego prawidłowego zestawu danych wierzycieli i dłużników. Nie zwraca on jednak takich samych wyników, jak sugerują testy w zadaniu rekrutacyjnym. Liczba transakcji jest jednak zachowana.

## Worker

### Idea

Worker działa na zasadzie zwykłej pętli, która wykonuje cztery główne kroki.

1. Pobierz klucz `debts_id` z SQS
2. Pobierz plik CSV o podanym kluczu z S3
3. Zoptymlizuj transakcje
4. Podaj wynik optymaliacji do S3 pod kluczem pochodnym (`+_results`).

### Pobieranie klucza z SQS

Worker pobiera odpowiedź z kolejki, jeżeli w body odpowiedzi nie ma pola "debts_id" (kolejka jest pusta), to czeka sekundę i powtarza krok.

### Pobieranie danych z S3

Worker pobiera dane do `BytesIO`, który następnie jest przekształcony do `StringIO`, by można było użyć `csv.reader` tak samo, jak w części pierwszej zadania rekrutacyjnego.

### Optymalizacja

Ten krok jest identyczny jak w części pierwszej zadania.

### Wysyłanie danych do S3

Po optymaliacji Worker zapisuje przy pomocy `csv.writer` listę płatności do strumienia typu `StringIO`, który następnie przekształcany jest do `BytesIO` i wysyłany do S3 pod kluczem postaci `{debts_id}_results`.

### Podsumowanie Workera

Worker jest prostą implementacją serwisu, która próbuje pobrać dane z kolejki, a jeżeli kolejka jest pusta, czeka przez sekundę i następnie uaktalnie dane w S3.
