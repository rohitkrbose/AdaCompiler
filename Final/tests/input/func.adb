procedure func is
	procedure Aviraj (R: integer) is
		nn : integer;
	begin
		nn := 23;
		nn := R + nn;
		print_int (nn);
	end;
	procedure Mkk (A, B : integer) is
		u : integer;
	begin
		print_int (A);
		print_int (B);
		Aviraj (5);
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
		z := 82;
		print_int (z);
		Mkk(z,9);
	end;
begin
	main;
end;