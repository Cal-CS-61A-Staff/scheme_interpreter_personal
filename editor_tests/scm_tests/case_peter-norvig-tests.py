from scheme_runner import SchemeTestCase, Query

cases = [
    SchemeTestCase([Query(code=['(define (square x) (* x x))'], expected={}),
                    Query(code=['(define double (lambda (x) (* 2 x)))'], expected={}),
                    Query(code=['(double 5)'], expected={'out': ['10\n']}),
                    Query(code=['(define compose (lambda (f g) (lambda (x) (f (g x)))))'], expected={}),
                    Query(code=['((compose list double) 5)'], expected={'out': ['(10)\n']}),
                    Query(code=['(define apply-twice (lambda (f) (compose f f)))'], expected={}),
                    Query(code=['((apply-twice double) 5)'], expected={'out': ['20\n']}),
                    Query(code=['((apply-twice (apply-twice double)) 5)'], expected={'out': ['80\n']}),
                    Query(code=['(define fact (lambda (n) (if (<= n 1) 1 (* n (fact (- n 1))))))'], expected={}),
                    Query(code=['(fact 3)'], expected={'out': ['6\n']}),
                    Query(code=['(fact 50)'], expected={
                        'out': ['30414093201713378043612608166064768844377641568960512000000000000\n']}),
                    Query(
                        code=['(define (combine f)', '(lambda (x y)', '(if (null? x) nil', '(f (list (car x) (car y))',
                              '((combine f) (cdr x) (cdr y))))))'], expected={}),
                    Query(code=['(define zip (combine cons))'], expected={}),
                    Query(code=['(zip (list 1 2 3 4) (list 5 6 7 8))'],
                          expected={'out': ['((1 5) (2 6) (3 7) (4 8))\n']}),
                    Query(
                        code=['(define riff-shuffle (lambda (deck) (begin',
                              '(define take (lambda (n seq) (if (<= n 0) (quote ()) (cons (car seq) (take (- n 1) (cdr seq))))))',
                              '(define drop (lambda (n seq) (if (<= n 0) seq (drop (- n 1) (cdr seq)))))',
                              '(define mid (lambda (seq) (/ (length seq) 2)))',
                              '((combine append) (take (mid deck) deck) (drop (mid deck) deck)))))'], expected={}),
                    Query(code=['(riff-shuffle (list 1 2 3 4 5 6 7 8))'], expected={'out': ['(1 5 2 6 3 7 4 8)\n']}),
                    Query(code=['((apply-twice riff-shuffle) (list 1 2 3 4 5 6 7 8))'],
                          expected={'out': ['(1 3 5 7 2 4 6 8)\n']}),
                    Query(code=['(riff-shuffle (riff-shuffle (riff-shuffle (list 1 2 3 4 5 6 7 8))))'],
                          expected={'out': ['(1 2 3 4 5 6 7 8)\n']}),
                    Query(code=["(apply square '(2))"], expected={'out': ['4\n']}),
                    Query(code=["(apply + '(1 2 3 4))"], expected={'out': ['10\n']}),
                    Query(code=["(apply (if false + append) '((1 2) (3 4)))"], expected={'out': ['(1 2 3 4)\n']}),
                    Query(code=['(if 0 1 2)'], expected={'out': ['1\n']}),
                    Query(code=["(if '() 1 2)"], expected={'out': ['1\n']}),
                    Query(code=['(or false true)'], expected={'out': ['#t\n']}),
                    Query(code=['(or)'], expected={'out': ['#f\n']}),
                    Query(code=['(and)'], expected={'out': ['#t\n']}),
                    Query(code=['(or 1 2 3)'], expected={'out': ['1\n']}),
                    Query(code=['(and 1 2 3)'], expected={'out': ['3\n']}),
                    Query(code=['(and false (/ 1 0))'], expected={'out': ['#f\n']}),
                    Query(code=['(and true (/ 1 0))'], expected={'out': ['Error\n']}),
                    Query(code=['(or 3 (/ 1 0))'], expected={'out': ['3\n']}),
                    Query(code=['(or false (/ 1 0))'], expected={'out': ['Error\n']}),
                    Query(code=['(or (quote hello) (quote world))'], expected={'out': ['hello\n']}),
                    Query(code=['(if nil 1 2)'], expected={'out': ['1\n']}),
                    Query(code=['(if 0 1 2)'], expected={'out': ['1\n']}),
                    Query(code=['(if (or false false #f) 1 2)'], expected={'out': ['2\n']}),
                    Query(code=['(define (loop) (loop))'], expected={}),
                    Query(code=['(cond (false (loop))', '(12))'], expected={'out': ['12\n']}),
                    Query(code=['((lambda (x) (display x) (newline) x) 2)'], expected={'out': ['2\n2\n']}),
                    Query(code=['(define g (mu () x))'], expected={}),
                    Query(code=['(define (high f x)', '(f))'], expected={}),
                    Query(code=['(high g 2)'], expected={'out': ['2\n']}),
                    Query(code=['(define (print-and-square x)', '(print x)', '(square x))'], expected={}),
                    Query(code=['(print-and-square 12)'], expected={'out': ['12\n144\n']}),
                    Query(code=['(/ 1 0)'], expected={'out': ['Error\n']}),
                    Query(code=['(define addx (mu (x) (+ x y)))'], expected={}),
                    Query(code=['(define add2xy (lambda (x y) (addx (+ x x))))'], expected={}),
                    Query(code=['(add2xy 3 7)'], expected={'out': ['13\n']}),
                    Query(code=['(remainder -5 4)'], expected={'out': ['-1\n']}),
                    Query(code=['(remainder 5 -4)'], expected={'out': ['1\n']}),
                    Query(code=['(remainder -5 -4)'], expected={'out': ['-1\n']}),
                    Query(code=['(define (len s)', "(if (eq? s '())", '0', '(+ 1 (len (cdr s)))))'], expected={}),
                    Query(code=["(len '(1 2 3 4))"], expected={'out': ['4\n']})])
]
