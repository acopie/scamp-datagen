def sir_special(sir):
    """
    Funcția ord() întoarce codul ASCII al unui caracter. Care dintre următoarele afirmații sunt adevărate:
    - (F) Funcția sir_special() verifică dacă orice cuvânt este palindrom
    - (A) Dacă se înlocuiește condiția  ciclului while cu i<j comportamentul este același dar în unele
          cazuri micșorăm numărul de comparații realizate în funcție
    - (F) Dacă se înlocuiește condiția  ciclului while cu i<j comportamentul este același dar în unele
          cazuri mărim numărul de comparații realizate în funcție
    - (F) Dacă se înlocuiește condiția  ciclului while cu i<j comportamentul este diferit
    - (A) Din lista ['Miss', 'Arora', 'teaches', 'us', 'malayalam', 'bdwy'] 3 cuvinte îndeplinesc properietatea
          verificată de functia sir_special()
    - (F) Din lista ['Miss', 'Arora', 'teaches', 'us', 'malayalam', 'bdwy'] 4 cuvinte îndeplinesc properietatea
          verificată de functia sir_special()
    """
    # i = 1
    # n = len(sir)-1
    # j=n-1
    # #sir = sir.lower()
    # #while i<n and j>=0:
    # while i<=j:
    #     if abs(ord(sir[i])-ord(sir[i-1])) != abs(ord(sir[j])-ord(sir[j+1])):
    #         return False
    #     i+=1
    #     j-=1
    # return True
    i = 2
    n = len(sir) - 1
    j = n - 1
    # sir = sir.lower()
    # while i<n and j>=0:
    while i <= j:
        if abs(ord(sir[i]) - ord(sir[i - 1])) != abs(ord(sir[j]) - ord(sir[j + 1])):
            return False
        i += 1
        j -= 1
    return True

l=[' Miss', ' Arora', ' teaches', ' us', ' malayalam', ' bdawy']
#l=['Proln', 'ne', 'invata', 'despre', 'lupul', "Siberian"]

print(ord('A')-ord('d'), ord('d')-ord('e'))

for el in l:
    if sir_special(el):
        print(el)

"""
Care dintre următoarele afirmații sunt adevărate: valoare nu e divizibil cu k si h in accelasi timp

- (A) Pentru șirul de valori 24, 25, 49, 28, -28, 14 se va afișa 14 49 25 24
- (F) Pentru șirul de valori 24, 25, 49, 28, -28, 14 se va afișa 24 25 49 14
- (A) Condiția din instrucțiunea if este echivalentă cu sir[n]%k != 0 or sir[n]%h != 0 -- echivalenta in cod
- (F) Condiția din instrucțiunea if este echivalentă cu sir[n]%k != 0 and sir[n]%h != 0
"""
def afisare(sir, n, k, h):
    if n < 0:
        return
    #if not (sir[n]%k == 0 and sir[n]%h == 0):
    a = sir [n]
    if a<0: a=-a
    if a % k != 0 or a % h != 0:
        print(sir[n])
    afisare(sir, n-1, k, h)

l = [24, -25, 49, 28, -28, 14, 12,56]
afisare(l, len(l)-1, -4, 28)

"""
Se dă un șir, a, cu k elemente (ex. a=[1,2,3]). Să se identifice algoritmul/algoritmi care populează o matrice b cu 
nxm elemente astfel: completează matricea pe linii cu elementele șirului a, dacă nu mai sunt element în șirul a, va 
completa cu șirul a inversat
1 2 3 3
2 1 1 2
3 3 2 1
"""
def afisare_mat(b,n,m):
    print(b)
    for i in range(1,n+1):
        for j in range(1,m+1):
            print(b[i][j], end=' ')
        print()

def completare1( a, k, n, m): #NOK
    b=[[-1]*(m+1) for _ in range(n+1)]
    h = 1
    d_cresc = 1
    for i in range(1,n+1):
        for j in range(1,m+1):
            b[i][j] = a[h]
            h += d_cresc
            if h == k or h == 1:
                d_cresc = -d_cresc
    afisare_mat(b, n, m)
print("#####Completare1")
completare1([-1, 1,2,3], 3, 3, 4)

def completare2( a, k, n, m): #NOK
    b=[[0]*(m+1) for _ in range(n+1)]
    h = 1
    d_cresc = -1
    for i in range(1,n+1):
        for j in range(1,m+1):
            if h == k or h == 1:
                d_cresc = -d_cresc
            b[i][j] = a[h]
            h += d_cresc
    afisare_mat(b, n, m)
print("#####Completare2")
completare2([0, 1,2,3], 3, 3, 4)

def completare3( a, k, n, m): #OK
    b=[[0]*(m+1) for _ in range(1+n)]
    h=-1
    d_cresc = -1
    for i in range(1,n+1):
        for j in range(1,m+1):
            print(f"({i}, {j})", ((i-1)*(m)+(j-1)) % (k), (i*(m)+j) , (k+1) )
            if ((i-1)*(m)+(j-1)) % (k) == 0:
                d_cresc = -d_cresc
                if d_cresc == 1: h=1
                else: h = k
            b[i][j] = a[h]
            h += d_cresc


    afisare_mat(b, n, m)

print("#####Completare3")
completare3([0, 1,2,3], 3, 3, 4)

def completare4( a, k, n, m): #OK
    b=[[0]*(m+1) for _ in range(n+1)]
    h=0
    d_cresc = -1
    for i in range(1,1+n):
        for j in range(1,1+m):
           if h == 0:
                    h=1
                    d_cresc = -d_cresc
           elif h == k+1:
                    h = k
                    d_cresc = -d_cresc
           b[i][j] = a[h]
           h += d_cresc


    afisare_mat(b, n, m)

print("#####Completare4")
completare4([0, 1,2,3], 3, 3, 4)

"""
Se da o matrice pătratica. Sa se verifice ca elementele de sub diagonala principala se reflecta deasupra diagonalei
1 2 3 4
2 1 5 6
3 5 1 7
4 6 7 1


Se dau fct verifica_mat1(), verifica_mat2(), verifica_mat3()
- [A] Toate cele 3 funcții verifică aceeași proprietate
- [F] Nu toate cele 3 funcții verifică aceeași proprietate
- [A] In orice caz numărul de evaluări ale conditiei instructiuni if este egal pentru functiile verifica_mat1(), verifica_mat2()
   daca matricea verifica propietate
- [F] In orice caz numărul de evaluări ale conditiei instructiuni if este egal pentru functiile verifica_mat1(), verifica_mat2()
   daca matricea nu verifica propietate
"""
comp1=0
comp2=0
comp3=0
def verifica_mat1(a, n): #ok
    global comp1
    for i in range(1, n):
        for j in range(i+1,n+1):
            comp1 += 1
            if a[i][j] != -a[j][i]:
                return False
    return True
mat = [[0,0,0,0,0], [0,2,2,3,4],[0,-2,1,-5,6],[0,-3,5,9,7],[0,-4,-6,-7,1]]

print(verifica_mat1(mat,4))

def verifica_mat2(a, n):#ok
    global comp2
    for i in range(n-1,0,-1):
        for j in range(n, i,-1):
            comp2+=1
            if a[i][j] != -a[j][i]:
                return False
    return True

print(verifica_mat2(mat,4))

def verifica_mat3(a, n):#ok
    global comp3
    for i in range(1, n+1):
        for j in range(1, n+1):
            comp3+=1
            if a[i][j] != -a[j][i] and i!=j:
                return False
    return True

print(verifica_mat3(mat,4))

print("comp1", comp1,"comp2", comp2,"comp3", comp3)


