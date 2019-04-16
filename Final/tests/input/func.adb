procedure func is
	procedure Mkk (A, B : integer) is
		u : integer;
		j : float;
	begin
		print_int (A);
		-- if A <= B then
		-- 	A := 5;
		-- else
		-- 	A := 6;
		-- end if;
		-- print_int (A);
	end;
	procedure main is
		z : integer;
	begin
		z := 8;
		Mkk(z,9);
	end;
begin
	main;
end;