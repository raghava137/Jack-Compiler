import sys
def main_exec():
    if len(sys.argv)!=2:return
    x={"comp":{"0":"0101010","1":"0111111","-1":"0111010","D":"0001100","A":"0110000","!D":"0001101","!A":"0110001","-D":"0001111","-A":"0110011","D+1":"0011111","A+1":"0110111","D-1":"0001110","A-1":"0110010","D+A":"0000010","D-A":"0010011","A-D":"0000111","D&A":"0000000","D|A":"0010101","M":"1110000","!M":"1110001","-M":"1110011","M+1":"1110111","M-1":"1110010","D+M":"1000010","D-M":"1010011","M-D":"1000111","D&M":"1000000","D|M":"1010101"},"dest":{"":"000","M":"001","D":"010","MD":"011","A":"100","AM":"101","AD":"110","AMD":"111"},"jump":{"":"000","JGT":"001","JEQ":"010","JGE":"011","JLT":"100","JNE":"101","JLE":"110","JMP":"111"}}
    y={f"R{i}":i for i in range(16)}
    y.update({"SP":0,"LCL":1,"ARG":2,"THIS":3,"THAT":4,"SCREEN":16384,"KBD":24576})
    z=16
    with open(sys.argv[1],'r') as a:
        b=[c.split('//')[0].strip() for c in a if c.split('//')[0].strip()]
    d=0
    for e in b:
        if e.startswith('('):y[e[1:-1]]=d
        else:d+=1
    f=[]
    for g in b:
        if g.startswith('('):continue
        if g.startswith('@'):
            h=g[1:]
            if not h.isdigit():
                if h not in y:
                    y[h]=z
                    z+=1
                h=y[h]
            f.append(f"{int(h):016b}")
        else:
            i,j=g.split('=') if '=' in g else ("",g)
            k,l=j.split(';') if ';' in j else (j,"")
            f.append(f"111{x['comp'].get(k,'0000000')}{x['dest'].get(i,'000')}{x['jump'].get(l,'000')}")
    with open(sys.argv[1].replace('.asm','.hack'),'w') as m:
        m.write('\n'.join(f)+'\n')
if __name__=="__main__":
    main_exec()