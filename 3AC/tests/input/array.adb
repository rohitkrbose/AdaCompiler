procedure demo is
	squares: array (1 .. 10, 1 .. 5) of Integer;
	i : Integer;
	begin
		i := 1;
		squares ( i , 5 ) := i * 2;
		i := squares ( i , 5 );
	end;