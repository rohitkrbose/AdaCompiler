procedure func is
	type Car is record
		Identity       : integer;
		Consumption    : float;
	end record;
	procedure Mkk (A, B : integer; C: float) is
		Cw : Car;
		z : integer;
	begin
		print_int (A);
		if A <= B then
			A := 5;
		else
			A := 6;
		end if;
		print_int (A);
	end;
	procedure main is
		j : integer;
	begin
		j := 8;
		Mkk(j,9,3.56);
	end;
begin
	main;
end;