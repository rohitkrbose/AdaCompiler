procedure demo is
	squares: array (1 .. 10 , 1 .. 20) of Integer;
	i : Integer;
	begin
		i := 1;
		squares ( i , i ) := i * 2;
	end demo;