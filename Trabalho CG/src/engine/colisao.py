def colisaoINI(a,b):
    return not (a[3]<b[0] or a[0]>b[3] or
                a[4]<b[1] or a[1]>b[4] or
                a[5]<b[2] or a[2]>b[5])
