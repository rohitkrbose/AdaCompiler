procedure fibonacci is
	function Aviraj (R: integer) return integer is
		nn : integer;
	begin
		nn := 23;
		nn := R + nn;
		return nn;
	end;
	procedure Mkk (A, B : integer) is
		u : integer;
	begin
		print_int (A);
		print_int (B);
		u := Aviraj (5);
		print_int (u);
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