from pprint import pprint

def get_distance(a,b):
    # print(a,b)
    i = len(a)
    j = len(b)
    # print(i,j)
    if i==0:
        return j
    elif j==0:
        return i
    else:
        if a[0] == b[0]:
            return get_distance(a[1:],b[1:])
        else:
            return min(1+get_distance(a,b[1:]),1+get_distance(a[1:],b),2+get_distance(a[1:],b[1:]))

def get_distance_dyn(a,b):
    # print(a,b)
    m = len(a)
    n = len(b)
    outarr = [[None]*(n+1) for i in range(m+1)]

    for i in range(m+1):
        for j in range(n+1):
            if i == 0:
                outarr[i][j] = j
            elif j == 0:
                outarr[i][j] = i
            else:
                if a[i-1] == b[j-1]:
                    outarr[i][j] = outarr[i-1][j-1]
                else:
                    outarr[i][j] =min(1+outarr[i][j-1],1+outarr[i-1][j],2+outarr[i-1][j-1])
    return outarr[m][n]

    # print(i,j)
    # if i==0:
    #     return j
    # elif j==0:
    #     return i
    # else:
    #     if a[0] == b[0]:
    #         return get_distance(a[1:],b[1:])
    #     else:
    #         return min(1+get_distance(a,b[1:]),1+get_distance(a[1:],b),2+get_distance(a[1:],b[1:]))


if __name__ == "__main__":
    # a='a'
    # print(a[1:])
    pprint(get_distance_dyn('alisowildfkldfjlkadfern','wilderlakdfjlalisodlkfdajlsjlan'))
    # print(get_distance('alisowildern','wilderalison'))
