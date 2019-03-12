procedure func is
    i : integer := 2;
    procedure foo is
        i : integer := 1;
    begin
        null;
        printi(i);
        for j in 1 .. 5 loop
            prints("I have a null statement");
        end loop;
    end foo;
begin
    foo;
    i := i * 2;
end func;

